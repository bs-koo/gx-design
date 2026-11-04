# GX 평가 러너

`run_eval.py`는 Codex CLI JSONL 이벤트와 파일 내용 해시를 기록한다. 대화 상태는 평가 전용 sidecar로 받고, 현재 질문에 정확히 대응하는 답만 전송한다. 표준 라이브러리만 사용한다.

| 구성 | 역할 |
|---|---|
| `dialogue-scenarios/T01–T21*.json` | 승인된 제안의 21개 수용 사례. 실제 모델 실행은 아직 하지 않은 검토용 fixture |
| `scenarios/*.json` | 기존 4개 시나리오. 스키마·비용 기록 호환용 legacy 자료 |
| `run_eval.py` | 질문 상태별 응답, 종료 이유, 사용량, 해시·이벤트 기록 |
| `score.py`, `rubric.md` | 절차·대화·실물 점수를 분리해서 집계 |
| `../tests/test_eval_dialogue.py` | 모델 호출 없는 결정론적 회귀 검사 |

## 실행

```powershell
python -m unittest discover -s tests -p test_eval_dialogue.py -v
python evals/run_eval.py --scenario-dir evals/dialogue-scenarios --dry-run
python evals/run_eval.py --scenario-dir evals/dialogue-scenarios --scenario T11 --mode core --dry-run
```

실제 실행은 위 명령의 `--dry-run`을 제거하고 필요하면 `--codex-home <격리 홈>`을 추가한다. 실제 모델 호출은 유료이며, 호출 수·모델·브리프·브랜드·데이터·환경·예산·반복 표본을 기록해 비교한다. dry-run은 조건부 checkpoint와 최초 명령만 보여주며 모델을 실행하거나 결과를 만들지 않는다. `review_cases`는 사람이 확인할 하위 변형이며 러너가 자동 확장하는 실행 목록이 아니다. T04의 빈 응답·취소·기본 옵션, T09의 중단·진행 위임, T20의 명세·MP4 변형은 각각 별도 실행으로 확인해야 한다.

기본 작업 폴더는 새 `evals/results/<timestamp>/work/<scenario>-<mode>/`다. fixtures는 저장소 상대 `src`에서 작업 폴더 상대 `dest`로 복사한다. 저장소와 겹치는 작업 폴더나 기존 파일이 있는 작업 폴더는 거부한다. 옵션은 `--scenario`, `--scenario-dir`, `--mode core|full|both`, `--workdir`, `--results-dir`, `--max-turns`, `--timeout`, `--codex-bin`이다. `evals/results/`는 gitignore 대상이다.

격리 CODEX_HOME에 평가할 플러그인 버전을 설치하고 로그인한다. 하위 프로세스에만 CODEX_HOME이 설정된다. 인증 파일은 커밋하지 않는다. 기본 workspace-write 환경에서는 새 복사본으로 실행한다. read-only 환경이 sidecar 기록까지 막으면 이 프로토콜을 완료할 수 없으므로 `missing_signal`로 종료한다.

## 시나리오와 checkpoint

공통 키는 `id`, `skill`(gx-design|gx-redesign), `request`, `mode`(core|full), `max_turns`, `expected`다. 새 시나리오는 `answers` 대신 아래 `dialogue`를 둔다. 기존 `answers` 키는 호환을 위해 읽되 승인으로 변환하지 않는다.

```json
{
  "dialogue": {
    "version": 1,
    "checkpoints": [
      {
        "decision": {"id": "direction", "type": "selection", "scope_version": "v1"},
        "response": {"status": "answered", "value": "A를 선택할게"}
      }
    ]
  }
}
```

checkpoint는 순서대로 소비하되 현재 pending의 `id/type/scope_version`이 모두 일치해야 한다. 관련 없는 질문, 예전 범위 버전 또는 다른 종류의 결정에는 답을 주입하지 않는다. 동일 결정의 재질문은 별도 checkpoint가 있어야 다시 답한다. 체크포인트 목록은 테스트 준비물이며 질문하거나 승인할 이유가 아니다.

응답 상태는 `answered`, `delegated`, `partial`, `empty`, `cancelled`, `rejected`, `status_query`, `stopped`, `scope_change`다. `answered/delegated/scope_change`는 명시적 문자열 값이 필요하다. 빈 응답·취소·부분 답변·상태 질문을 승인으로 채우지 않는다. 러너는 `[Evaluator reply]` JSON에 결정과 응답 상태를 담아 전송한다. 답변을 보내지 않는 무응답 사례는 checkpoint를 비워 둔다.

범위 변경으로 필수 결정을 폐기하는 권한은 **시나리오에 명시한 사용자 응답**에서만 나온다. 해당 checkpoint의 `response`를 아래처럼 작성한다. `invalidates`는 `scope_change`에만 허용되며, 어시스턴트가 추측해서 추가할 수 없다.

```json
{
  "status": "scope_change",
  "value": "방향 선택은 철회하고 점검만 해줘.",
  "invalidates": [
    {"id": "direction", "type": "selection", "scope_version": "v1", "reason": "사용자가 방향 선택을 철회함"}
  ]
}
```

## 평가 전용 상태 신호

러너는 각 턴 프롬프트에 새 `GX_EVAL_NONCE`와 계측 지시를 붙인다. 어시스턴트/도구 어댑터는 종료 전에 작업 폴더의 `.gx-eval-state.json`을 기록한다. 이 신호는 제품 사용자의 질문·납품물에 추가하는 요소가 아니다. 임의 자연어에서 질문이나 승인을 추측하지 않는다.

```json
{
  "protocol": "gx-eval-dialogue/v1",
  "nonce": "현재 턴의 GX_EVAL_NONCE 값",
  "state": "waiting",
  "pending": [
    {"id": "direction", "type": "selection", "scope_version": "v1", "required": true, "status": "unresolved"}
  ]
}
```

state는 `waiting/completed/stopped/unverified`, pending status는 `unresolved/partial`이다. waiting에는 pending이 있어야 하고, completed에는 미확정 필수 결정이 없어야 한다. nonce가 다르거나 신호가 없거나 잘못되면 중단한다. 필수 pending은 러너에도 누적되며, 해당 결정의 answered/delegated 응답 전송 없이 사라졌다는 주장만으로 완료되지 않는다. 범위 변경으로 폐기하려면 먼저 정확히 매칭된 scripted `scope_change` 응답이 전송되어야 한다. 이후 sidecar `invalidated`의 `id/type/scope_version/reason` 네 필드가 scripted `invalidates`와 모두 같을 때만 1회 폐기한다. 모델이 만든 이유, 다른 결정·버전·종류·이유, 무응답·취소·부분·상태 질문 뒤의 독자적 폐기는 `unauthorized_invalidation`이다. 폐기는 다른 결정을 승인하지 않는다.

완료는 자연어의 '완료', 물음표 부재 또는 `turn.completed` 이벤트로 판정하지 않는다. 신선한 `state: completed`가 있어야 하며, 남은 checkpoint는 보내지 않는다. 이 신호는 모델의 상태 보고이므로 파일 품질이나 권한 준수의 독립 증거가 아니다. 사람이 원본 질문·답변·산출물·이벤트를 대조해야 한다.

| stop_reason | 의미 |
|---|---|
| `completed` | 명시적 대화 완료. 과업·실물 품질 통과는 별도 채점 |
| `waiting` | 일치하는 다음 답변이 없어서 실제 대기 |
| `unexpected_question` | 다음 checkpoint와 현재 결정이 불일치 |
| `missing_signal`, `stale_or_invalid_signal`, `invalid_signal` | 상태를 신뢰할 수 없음 |
| `unresolved_required` | 필수 결정의 미응답 상태가 남아 있음 |
| `unauthorized_invalidation` | scripted scope_change 권한과 정확히 대응하지 않는 폐기 주장 |
| `max_turns`, `stopped`, `unverified`, `error_turn_N` | 미완료·중단·필수 증거 부족·실행 실패 |
| `legacy_unbound_answers` | 기존 답 목록에 현재 질문을 매칭할 정보가 없음 |

기존 4개 시나리오는 그대로 로드·실행·dry-run할 수 있다. **Legacy 제한:** `answers`는 결정 ID·종류·범위 버전이 없으므로 자동 전송하지 않는다. 질문이 나오면 `legacy_unbound_answers`로 중단한다. checkpoint를 사람이 대응시켜 추가한 뒤에만 다중 턴 평가로 사용한다. 과거 `answers_exhausted`, `max_turns` 또는 종료 이유 없는 결과는 완료 증거가 없어 성공 평균에서 제외한다.

## 증거와 점수

결과 JSON에는 각 턴의 프롬프트·마지막 메시지·상태 신호, 도구 수, 사용량, `files`, `file_hashes_before/after`, `mutation_events`가 남는다. 원본 JSONL과 턴별 마지막 메시지도 보존한다. `snapshot()`의 경로→2개 값 튜플 구조는 유지하며 두 번째 값은 mtime 대신 SHA-256이다. JSON에서는 `[size_bytes, sha256]`가 된다. 평가 sidecar는 산출물 diff에서 제외한다.

파일 내용 해시는 같은 크기·같은 시각의 변경을 잡는다. 가능한 `file_change`·명령 이벤트는 턴 중 수정 후 복구도 기록한다. **관측 한계:** 임의 shell의 쓰기 후 복구, 작업 폴더 밖 파일, 누락 이벤트와 원격 도구는 보이지 않을 수 있다. 깨끗한 해시와 어시스턴트의 '수정 안 함' 주장만으로 모든 순간의 무단 변경이 없었다고 판정하지 않는다. 필요한 환경에서는 독립 파일 감시·도구 기록을 보완한다.

`turn.completed` usage가 단조 증가하면 마지막 누적값과 턴별 차이를 기록하고, 아니면 합산한다. 호스트의 턴 단위 usage가 우연히 단조 증가하는 경우는 이 기존 추정으로 구별할 수 없으므로 원본 이벤트와 호스트 버전을 함께 확인한다. 토큰 0은 정보 누락일 수도 있다.

`time.perf_counter()`로 각 CLI 호출의 `turns[].elapsed_seconds`와 그 합계 `turn_elapsed_seconds`를 기록한다. 실행 전체 `elapsed_seconds`는 작업 폴더 준비부터 결과 객체 조립까지의 단조 시계 경과 시간이다. 준비·해시·이벤트 처리 시간을 포함하고 마지막 결과 파일 저장·출력은 제외한다. 이 값은 고정 응답을 즉시 전달하는 scripted 실행 시간으로, 실제 사용자 응답 대기 시간은 포함하지 않는다. 시간 측정 기능 추가나 mocked 시계 테스트 통과만으로 실제 제작 시간이 단축됐다고 주장하지 않는다.

`python evals/score.py evals/results/<timestamp>`는 **completed 실행만** 성공 비용 평균에 넣고 나머지는 이유와 함께 별도 표시한다. 대기 동작이 정답인 T03 같은 사례도 완료 과업의 성공 비용 평균에는 섞지 않는다. 대화 준수의 기대 결과로는 별도 검토한다. 절차 6개 점수와 대화·실물 점수는 [rubric.md](rubric.md)에 따라 분리한다. 과업 실패나 조기 실행 위반을 미감 평균으로 덮지 않는다.

2026-10-15의 legacy 시범 기록은 03/core 3턴, 도구 19회, 입력 1,159,958(캐시 1,076,608), 출력 7,718 tokens였다. 고정 답변 주입이 있는 과거 실행이므로 현재 계약의 성공 근거로 사용하지 않는다. 이 러너의 자동 회귀 검사와 21개 fixture 등록은 실제 모델 개선·비전문 사용자 질문 이해도·두 호스트 동작의 검증을 대신하지 않는다.
