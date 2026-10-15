# gx-design 평가 세트

모드 설계(핵심/전체)와 버전 변경이 **비용**(토큰·턴·도구 호출)과 **품질**(채점표 점수)에 주는 영향을 추정이 아니라 실행 기록으로 비교하기 위한 세트다. Codex CLI 비대화 실행(`codex exec`)으로 시나리오를 돌린다.

## 구성

| 파일 | 역할 |
|---|---|
| `scenarios/*.json` | 시나리오 4개 — 쇼핑몰 가을 랜딩(신규 UI) / 15초 Reels(영상 명세) / site/index.html 애니메이션 점검(점검 전용) / 대시보드 리디자인(리디자인 UI) |
| `run_eval.py` | 러너 — 첫 요청 후 미리 정한 답을 순서대로 넣고 실행량을 기록 |
| `score.py` | 결과 JSON을 시나리오×모드 비용 표로 집계, 채점 파일을 합침 |
| `rubric.md` | 품질 채점표(6개 기준, 각 0~2점) |

시나리오는 YAML 의존을 피하려고 JSON으로 쓴다. 필수 키: `id`, `skill`(gx-design|gx-redesign), `request`, `mode`(core|full), `answers`(게이트 순서에 묶이지 않는 자연어 답 목록), `max_turns`, `expected`(체크 항목). 선택 키: `title`, `fixtures`(`{"src": 저장소 상대 경로, "dest": 작업 폴더 상대 경로}`).

`run_eval.py`와 `score.py`는 표준 라이브러리만 쓰는 Python 3 스크립트다.

## 비용 경고

전체 매트릭스(시나리오 4 × 모드 2 × 비교 버전 수)는 **실제 모델 호출**이라 비싸고 오래 걸린다. 시나리오 1개가 수십만 토큰을 쓸 수 있다. 먼저 아래 시범 1회로 러너가 동작하는지 확인하고, 매트릭스 실행 여부는 비용을 보고 사람이 정한다. 항상 `--dry-run`으로 명령을 먼저 확인한다.

## 시범 실행 1회

시나리오 (3) 점검 전용을 핵심 모드로 1회 — 비용이 가장 작다.

```powershell
python evals/run_eval.py --scenario 03-site-motion-audit --mode core --dry-run
python evals/run_eval.py --scenario 03-site-motion-audit --mode core --codex-home <격리-CODEX_HOME>
python evals/score.py evals/results/<timestamp>
```

- 작업 폴더: 실행마다 `evals/results/<timestamp>/work/<scenario>-<mode>/`를 새로 만들고 `fixtures`를 복사한다(시나리오 3은 `site/index.html` → `index.html`). `--workdir <경로>`로 상위 경로를 바꿀 수 있다.
- 결과: `evals/results/<timestamp>/<scenario>-<mode>.json`(턴 수·토큰 합계·도구 호출 수·턴별 마지막 메시지·생성/수정 파일 목록), 원본 이벤트 `<scenario>-<mode>.events.jsonl`, 턴별 마지막 메시지 `<scenario>-<mode>.turnN.last.md`.
- 옵션: `--mode core|full|both`(기본은 시나리오의 mode), `--sandbox`(기본 `workspace-write`), `--max-turns N`, `--timeout 초`, `--codex-bin 경로`.
- `evals/results/`는 `.gitignore` 대상이다. 결과를 공유하려면 집계 표만 옮긴다.

## 격리 CODEX_HOME

평소 설정·다른 플러그인·메모리가 결과에 섞이지 않게 **격리 CODEX_HOME**을 쓴다. `--codex-home`은 하위 codex 프로세스의 환경에만 `CODEX_HOME`을 설정한다.

1. 빈 폴더를 만들고 그 폴더를 `CODEX_HOME`으로 둔 셸에서 로그인한 뒤 평가할 버전의 플러그인을 설치한다(설치 절차는 [두 호스트 유지보수 안내](../docs/codex-skill-maintenance.md)).
2. 격리 홈의 `config.toml`에는 평소 홈의 신뢰 프로젝트 설정이 없다. 작업 폴더(또는 그 상위 `evals/results/`)를 **신뢰 프로젝트 항목**으로 추가해야 승인 대기 없이 실행된다.
3. Windows에서는 격리 홈에서 `read-only` 샌드박스가 셸 명령을 거부하는 경우가 있다. 기본값 `workspace-write`를 쓰고, 작업 폴더는 지워도 되는 복사본(러너가 만드는 폴더)으로 둔다.
4. **인증 파일을 커밋하지 않는다.** 격리 홈(`auth.json` 등)은 저장소 밖에 두거나, 저장소 안이면 `.gitignore`로 막는다.
5. 버전 비교는 버전마다 격리 홈을 따로 만들어 플러그인 캐시가 섞이지 않게 한다.

## 품질 채점

[rubric.md](rubric.md)에 따라 산출물만 보고 매긴 결과를 `<scenario>-<mode>.scores.json`으로 결과 JSON 옆에 두면 `score.py` 표의 품질 열에 합쳐진다. 가능하면 채점자에게 모드·버전을 가린다.

## 해석 주의

- **표본이 작다.** 같은 시나리오도 실행마다 달라진다. 1회 실행 차이로 결론 내지 말고 n을 함께 보고, 차이가 실행 간 편차보다 클 때만 의미를 둔다.
- 미리 정한 답(`answers`)은 실제 사용자의 선택을 대신한다. 질문 수·순서가 달라지면 답이 남거나 모자랄 수 있다 — 턴별 마지막 메시지로 대화가 의도대로 흘렀는지 확인한다(`stop_reason` 참고).
- 토큰 수는 Codex가 JSONL 이벤트에 내보낸 사용량을 합산한 값이다. 이벤트 형식이 바뀌면 0이나 누락이 나올 수 있으므로 원본 `.events.jsonl`로 확인한다. 캐시 입력 토큰은 비용 계산 방식이 다르므로 따로 본다.
- 이 세트는 Codex 경로만 잰다. Claude Code 경로의 비용·품질은 별도로 확인해야 한다.
