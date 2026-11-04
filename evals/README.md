# GX 평가 러너

`run_eval.py`는 Codex CLI JSONL 이벤트와 파일 내용 해시를 기록한다. 대화 상태는 평가 전용 sidecar로 받고, 현재 질문에 정확히 대응하는 답만 전송한다. 표준 라이브러리만 사용한다.

| 구성 | 역할 |
|---|---|
| `dialogue-scenarios/T01–T23*.json` | 승인된 제안의 23개 수용 사례. 실제 모델 실행은 아직 하지 않은 검토용 fixture |
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

`src`와 지정한 `dest`는 비어 있지 않은 상대경로 문자열이어야 한다. 절대경로·드라이브 상대경로·`..`를 거부하고, 모든 fixture의 실제 경로가 각각 저장소와 작업 폴더 안에 있는지 **첫 폴더 생성·복사 전에** 검사한다. 디렉터리 fixture 안의 심볼릭 링크·junction과 원본 안으로 다시 복사하는 경로는 거부한다. 결과·이벤트·마지막 응답 파일도 실행 결과 폴더 바로 아래인지 검사한다.

격리 CODEX_HOME에 평가할 플러그인 버전을 설치하고 로그인한다. 하위 프로세스에만 CODEX_HOME이 설정된다. 인증 파일은 커밋하지 않는다. 기본 workspace-write 환경에서는 새 복사본으로 실행한다. read-only 환경이 sidecar 기록까지 막으면 이 프로토콜을 완료할 수 없으므로 `missing_signal`로 종료한다.

CLI는 Windows에서는 Job Object, POSIX에서는 별도 프로세스 그룹으로 실행한다. 시간 초과와 정상 종료 모두 남은 하위 작업을 종료하고, 실행 중인 관리 대상이 없음을 확인한 뒤 반환하여 파일 스냅샷을 확정한다. Windows wrapper는 Job 할당이 끝나기 전에는 실제 CLI를 시작하지 않으며 원본 stdout/stderr와 세션 이벤트를 그대로 전달한다. CLI 종료와 출력 파이프의 EOF를 별도로 확인하므로, 출력 연결을 상속한 자식이 남아 있어도 정상 종료를 시간 초과로 기록하지 않는다. 종료를 확인하지 못하면 결과를 확정하지 않고 오류를 낸다. **보장 범위:** POSIX에서 자식이 직접 새 세션으로 분리한 프로세스, 원격 작업과 외부 서비스는 프로세스 그룹 정리 대상 밖이다. 이런 실행에는 별도 환경 격리·취소 수단이 필요하다.

## 시나리오와 checkpoint

공통 키는 `id`, `skill`(gx-design|gx-redesign), `request`, `mode`(core|full), `max_turns`, `expected`다. 새 시나리오는 `answers` 대신 아래 `dialogue`를 둔다. 기존 `answers` 키는 호환을 위해 읽되 승인으로 변환하지 않는다.

`id`는 문자·숫자·`_`·`-`로 시작하고 이후 문자·숫자·`_`·`-`·`.`만 포함하는 파일명 한 요소다. 마지막 점과 Windows 예약 이름(`CON`, `NUL` 등)은 허용하지 않는다. 경로 구분자나 상위 경로를 id로 사용할 수 없다.

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

`turn.completed` usage가 관측된 키별로 단조 증가하면 키별 마지막 누적값과 턴별 차이를 기록하고, 아니면 합산한다. 빈 usage와 누락된 키는 기존 관측값·delta 기준을 지우지 않는다. 결과의 `usage_incomplete`, `usage_missing_turns`, `usage_missing_keys`는 관측 누락을 별도로 표시한다. 입력·출력 토큰은 최소 관측 키이며, 캐시·추론 등 선택 필드는 한 번도 제공되지 않았다는 이유만으로 누락으로 판정하지 않는다. 선택 필드가 일부 턴에만 제공되면 해당 공백도 기록한다. 표의 토큰 0은 실제 0 또는 미관측 기본값일 수 있으므로 이 메타데이터를 함께 확인한다. 불완전 표본은 관측된 값만 보존한 집계이며 전체 비용이나 절감 근거로 사용하지 않는다.

호스트의 턴 단위 usage가 우연히 단조 증가하는 경우는 이 기존 추정으로 누적 usage와 구별할 수 없다. 원본 이벤트와 호스트 버전을 함께 확인한다.

`time.perf_counter()`로 각 CLI 호출의 `turns[].elapsed_seconds`와 그 합계 `turn_elapsed_seconds`를 기록한다. 실행 전체 `elapsed_seconds`는 작업 폴더 준비부터 결과 객체 조립까지의 단조 시계 경과 시간이다. 준비·해시·이벤트 처리 시간을 포함하고 마지막 결과 파일 저장·출력은 제외한다. 이 값은 고정 응답을 즉시 전달하는 scripted 실행 시간으로, 실제 사용자 응답 대기 시간은 포함하지 않는다. 시간 측정 기능 추가나 mocked 시계 테스트 통과만으로 실제 제작 시간이 단축됐다고 주장하지 않는다.

`python evals/score.py evals/results/<timestamp>`는 **completed 실행만** 성공 비용 평균에 넣고 나머지는 이유와 함께 별도 표시한다. 비용 평균 자격과 채점 여부는 별개다. `waiting`·`stopped`·실패 실행의 절차·대화·실물 점수도 차원별 표본 수로 집계하며, 제외 행에도 저장된 점수를 표시한다. 대기 동작이 정답인 T03 같은 사례는 완료 과업의 성공 비용 평균에 섞지 않으면서 준수 점수를 남길 수 있다. 성공 비용 표본 중 사용량이 불완전한 수는 표에 별도 표시한다. 절차 6개 점수와 대화·실물 점수는 [rubric.md](rubric.md)에 따라 분리한다. 과업 실패나 조기 실행 위반을 미감 평균으로 덮지 않는다.

2026-10-15의 legacy 시범 기록은 03/core 3턴, 도구 19회, 입력 1,159,958(캐시 1,076,608), 출력 7,718 tokens였다. 고정 답변 주입이 있는 과거 실행이므로 현재 계약의 성공 근거로 사용하지 않는다. 이 러너의 자동 회귀 검사와 23개 fixture 등록은 실제 모델 개선·비전문 사용자 질문 이해도·두 호스트 동작의 검증을 대신하지 않는다.

## 선택적 첫 결과·재작업 시간 보고

성능을 조사할 때만 `benchmark.py`를 사용한다. 일반 디자인 실행에 추가 질문·문서·모델 호출을 만들지 않는다. 검토자가 실제 메시지·파일을 읽고 결과 JSON 옆에 같은 이름의 `.review.json`을 작성한다. 예: `T17-core.json` 옆의 `T17-core.review.json`.

```json
{
  "reviewer": "검토자 이름",
  "evidence": "2턴의 오류 문구가 요청 범위 안에서 바로 사용할 수 있음. 3턴은 발견한 문제의 재수정.",
  "first_useful_turn": 2,
  "rework_turns": [3]
}
```

```powershell
python evals/benchmark.py evals/results/<timestamp>/T17-core.json
python evals/benchmark.py evals/results/<timestamp>/T17-core.json --json --out outputs/timing-report.json
```

첫 유용 결과가 없거나 확인하지 못했으면 `first_useful_turn`은 `null`이다. 단순 진행 알림이나 모델의 완료 선언만으로 정하지 않는다. 도구는 선택한 턴 종료까지의 CLI 실행시간 합을 **상한 추정**으로 표시한다. 실제 첫 표시 시각·사람의 응답 대기시간과 구분하며, 재작업 횟수는 지정한 턴 수이므로 턴 내부 수정 횟수와도 다르다. 시간 누락은 0으로 채우지 않는다. 결과·검토 원본은 덮어쓰지 않는다.

전후 비교에는 같은 과업·브리프·브랜드·데이터·모델·호스트·환경의 반복 표본과 품질 판정을 함께 사용한다. 이 보고서 기능과 그 단위 검사 통과는 속도 개선율의 실측 증거가 아니다.
