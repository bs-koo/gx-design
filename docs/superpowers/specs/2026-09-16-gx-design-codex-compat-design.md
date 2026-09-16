# gx-design Codex 호환 설계

- 일자: 2026-09-16
- 대상: Claude Code 플러그인 `gx-design` 0.8.0
- 상태: 구현 계획의 기준 설계

## 목표와 성공 기준

현재 Claude Code에서 쓰는 6개 스킬을 Codex 플러그인에서도 발견하고 실행할 수 있게 한다. 신규 디자인과 기존 디자인 개선의 브리프 → 조사 → 전략 → 제작 → 검수 → 실물 제작 흐름을 두 호스트에서 유지한다. 이후 스킬을 수정할 때 담당자가 두 호스트의 매니페스트, 도구 호출, 위임, 참조 링크를 점검할 수 있는 한국어 참고문서와 자동 검사를 남긴다.

성공 기준은 다음과 같다.

1. `codex plugin marketplace add D:/SQ/design-plugin`과 `codex plugin add gx-design@gx-design`의 로컬 설치가 가능하고 새 대화에서 6개 스킬이 보인다.
2. 신규/개선 요청 각각에서 브리프 질문과 전략 선택을 호스트의 실제 입력 수단으로 진행한다. 입력 도구가 없거나 기능이 제한된 경우에도 대화로 선택을 받을 수 있다.
3. Codex에서 Claude 전용 `AskUserQuestion`, `Task`, 에이전트 파일의 `model: haiku|sonnet`, `skills:` 자동 주입을 필수 전제로 삼지 않는다. 병렬 위임은 실제로 제공된 서브에이전트 도구와 사용자·프로젝트 지시가 허용하는 범위에서만 한다.
4. 스킬을 고친 뒤 `python -m unittest discover -s tests`로 메타데이터, 기본 버전 동기화, 필수 참조, Claude 전용 도구 의존의 재발을 점검한다.
5. `README.md`와 `docs/codex-skill-maintenance.md`가 설치·업데이트·스킬 수정·검증 절차를 설명한다.

## 현황과 근거

저장소 루트에는 `.claude-plugin/plugin.json` 0.8.0과 `.claude-plugin/marketplace.json`, 6개 `skills/*/SKILL.md`, 3개 `agents/*.md`가 있다. 두 오케스트레이터와 참조 파일은 `AskUserQuestion`의 호출당 4문항, `multiSelect`, `preview`를 명시하고 이름이 고정된 Claude 서브에이전트를 스폰한다. 에이전트 frontmatter는 Claude 모델·도구·스킬 자동 주입을 설정한다. Codex용 매니페스트와 유지보수 검사는 없다.

OpenAI의 [Claude 플러그인 전환 안내](https://developers.openai.com/plugins/guides/submit-claude-plugin)는 스킬과 참조 파일을 유지하되 Claude 전용 지시문을 중립화하고 재사용 가능한 에이전트 절차를 스킬에 넣으라고 한다. [Codex 플러그인 안내](https://learn.chatgpt.com/docs/build-plugins)는 `.codex-plugin/plugin.json` 호환 매니페스트를 지원한다. [마켓플레이스 지원 형식](https://learn.chatgpt.com/docs/enterprise/plugin-management)은 기존 Claude 마켓플레이스를 지원하므로 저장소 구조를 바꿀 필요가 없다. [Codex 스킬 안내](https://learn.chatgpt.com/docs/build-skills)는 `name`과 `description`을 필수로 하고 실제 스킬을 `SKILL.md`에서 읽는다.

## 결정한 구조

`.codex-plugin/plugin.json`을 추가하고 기존 Claude 매니페스트와 `name`, 기본 `version`, `description`의 의미를 맞춘다. Codex 로컬 재설치용 `+codex.<cachebuster>` 접미사는 기본 버전을 바꾸지 않으므로 허용한다. Codex 마켓플레이스 파일을 새로 만들지 않고 `.claude-plugin/marketplace.json`을 설치 소스로 재사용한다. 공개 디렉터리 제출은 이번 범위에 넣지 않는다. 이 결정은 사용자의 검증 대상 답변이 오면 조정한다.

`skills/gx-design/HOST-COMPAT.md`는 실행 시점의 호스트 차이를 처리하는 작은 참조 파일이다. 질문은 실제로 제공된 구조화 입력 도구의 제한을 확인해 사용하고, 없으면 선택지를 대화에 제시한다. 브리프의 최종 승인과 전략 선택처럼 답변이 필요한 게이트는 답변을 받은 후 진행한다. 실물 제작은 사용자 선택이 필요한 경로 분기이므로 선택 전에 제작하지 않는다. 사용자가 이미 작업을 명시적으로 승인한 경우 불필요한 재승인으로 멈추지 않는다. 서브에이전트는 실제 도구·프로젝트 지시가 있을 때만 쓰며, 미가용이면 같은 절차를 주 에이전트가 수행한다. 외부 조사와 실물 렌더링은 환경의 실제 도구와 설치된 의존성에 맞춘다.

기존 `agents/*.md`는 Claude Code용으로 유지한다. Codex가 이 frontmatter를 해석한다고 가정하지 않도록 세 전문가의 역할·완료 기준 중 스킬에 없는 필수 사항을 `design-research`, `design-strategy`, `creative-production` 스킬에 넣는다. 오케스트레이터는 고정된 에이전트 이름 대신 역할과 입력·출력 계약을 지시한다. 사용 가능한 서브에이전트가 있으면 해당 역할을 위임하고, 없으면 스킬을 읽고 같은 일을 수행한다.

`tests/test_codex_compat.py`는 Python 표준 라이브러리만 사용해 변경 후 계약을 검사한다. 검사는 매니페스트 기본 버전 동기화, 6개 스킬의 메타데이터와 참조 파일 실재, 활성 스킬·참조 파일에 남은 `AskUserQuestion`·`WebSearch`·`WebFetch` 필수 호출과 Claude 모델 강제를 본다. 사용자 선택과 실제 디자인 품질은 정적 검사로 단정하지 않고 로컬 설치와 두 대표 시나리오로 검증한다.

## 파일 책임

| 파일 | 책임 |
|---|---|
| `.codex-plugin/plugin.json` | Codex 설치용 플러그인 메타데이터 |
| `skills/gx-design/HOST-COMPAT.md` | 질문·위임·도구 가용성의 실행 규칙 |
| `skills/gx-design/{SKILL,BRIEF-INTERVIEW,DESIGN-IT-TWICE,DESIGN-TONE-ANCHOR,REVIEW-AXES,PRODUCTION-HANDOFF,VISUAL-QUALITY}.md` | 신규 디자인 흐름의 호스트 중립 호출 |
| `skills/gx-redesign/{SKILL,REDESIGN-INTERVIEW}.md` | 개선 흐름의 호스트 중립 호출 |
| `skills/{design-research,design-strategy,creative-production}/SKILL.md` | 전문가 역할과 산출물 계약의 공통 정본 |
| `tests/test_codex_compat.py` | 두 호스트 공통 계약의 회귀 검사 |
| `docs/codex-skill-maintenance.md` | 추후 스킬 수정 절차와 검증표 |
| `README.md` | 사용자 설치·실행·업데이트 안내 |

## 범위와 검증

Claude 플러그인의 기존 명령어와 `agents/*.md`는 보존한다. 스킬의 디자인 방법론, 품질 기준, 산출물 형식은 호환에 필요한 문장 외에는 바꾸지 않는다. 외부 MCP, 새 이미지·영상 생성 의존성, 공개 플러그인 제출, 저장소 전체 재배치는 이번 작업에 포함하지 않는다.

먼저 표준 라이브러리 회귀 검사를 실패→통과 순서로 만든다. 다음에 Codex 매니페스트 검증기를 실행한다. 별도 `CODEX_HOME`을 `D:/Temp` 아래에 마련해 기존 사용자 설치를 건드리지 않고 로컬 마켓플레이스 설치를 확인한다. 마지막으로 새 대화에서 `gx-design`과 `gx-redesign`의 대표 요청을 실행해 브리프 질문, 전략 선택, 참조 파일 읽기, 위임 폴백을 점검한다. Claude Code에서는 기존 설치 경로와 두 스킬 진입 문구가 유지되는지 확인한다.
