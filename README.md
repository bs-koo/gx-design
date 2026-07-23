# gx-design — 디자인 멀티에이전트 팀 플러그인

BX · 그래픽 · UX/UI · 영상 프로젝트에 공통으로 쓰는 Claude Code 플러그인.
메인 세션이 AI Creative Director(오케스트레이터)가 되어 **브리프 인터뷰 게이트**(모호함이 사라질 때까지 AskUserQuestion 라운드)를 통과한 뒤 **Research → Strategy → Production → Review** 파이프라인을 전문 서브에이전트로 지휘한다.

## 구성

| 종류 | 이름 | 역할 |
|---|---|---|
| 스킬 | `gx-design` | 신규 디자인 진입점: 브리프 인터뷰 게이트 + 5단계 파이프라인 지휘 |
| 스킬 | `gx-redesign` | 기존 디자인 개선 진입점: 자산 인벤토리 → 진단(Audit) → 개선 파이프라인 지휘 |
| 스킬 | `design-research` | 리서치 방법론 (researcher에 사전 로드) |
| 스킬 | `design-strategy` | 전략 방법론 (strategist에 사전 로드) |
| 스킬 | `creative-production` | 제작 방법론 (producer에 사전 로드) |
| 스킬 | `creative-review` | 검수 기준 (producer 사전 로드 + 2축 검수에 사용) |
| 에이전트 | `design-researcher` (haiku) | 시장·사용자·경쟁사·트렌드 조사 → outputs/research/ |
| 에이전트 | `design-strategist` (sonnet) | 전략·콘셉트 수립 → outputs/strategy/ |
| 에이전트 | `creative-producer` (sonnet) | 명세·카피·프롬프트·프로토타입 제작 → outputs/production/ |

상세 절차는 참조 파일로 분리되어 있다:
gx-design/ — `BRIEF-INTERVIEW.md`(인터뷰 게이트) · `DESIGN-IT-TWICE.md`(전략 3안 병렬) · `REVIEW-AXES.md`(2·3축 독립 검수)
gx-redesign/ — `REDESIGN-INTERVIEW.md`(자산 인벤토리 + 개선 인터뷰)

## 설치

로컬 설치:

```
/plugin marketplace add D:\SQ\design-plugin
/plugin install gx-design@gx-design
```

원격(GitHub) 설치 — 팀원 공유용:

```
/plugin marketplace add bs-koo/gx-design
/plugin install gx-design@gx-design
```

설치·수정 후에는 Claude Code를 재시작해야 에이전트와 스킬이 인식된다.

## 설치 확인 (재시작 후)

```
현재 등록된 디자인 서브에이전트(design-researcher, design-strategist, creative-producer)와
스킬(gx-design, gx-redesign, design-research, design-strategy, creative-production, creative-review)을
역할·모델·도구·사전 로드 스킬 표로 확인해줘. 로드되지 않은 항목이 있으면 원인을 분석해줘.
```

## 사용

```
/gx-design:gx-design 대학생 캠퍼스 중고거래 서비스 UX/UI      ← 신규 제작 (5단계)
/gx-design:gx-redesign 커머스 앱 홈·상세 화면 리뉴얼          ← 기존 개선 (진단 선행 6단계)
```

또는 자연어로 요청하면 신규 제작/기존 개선을 판별해 해당 스킬이 자동 로드된다.

- 인터뷰는 결정 트리의 frontier 기준 — 지금 물을 수 있는 질문은 그 라운드에 전부 묻는다(도구 상한에 맞춰 4문항씩 분할 호출). 질문 수 총량 제한 없음.
- 인터뷰를 중단하려면 **"그만, 진행해"** — 미확정 항목은 [가정]으로 표기되고 진행된다.
- gx-redesign은 제작 전에 기존 디자인 진단(Audit)을 수행하고, 모든 변경을 before → after → 근거로 기록한다.
- 산출물: `outputs/brief|research|strategy|production|final/` (실행하는 프로젝트 기준, 저장 시 자동 생성)

## 수정 반영 (개발 워크플로)

플러그인은 **버전별로 캐시에 복사 설치**된다(`~/.claude/plugins/cache/gx-design/`). 파일만 수정하면 설치본에 반영되지 않는다:

1. `.claude-plugin/plugin.json`의 `version`을 올린다 (예: 0.1.1 → 0.1.2)
2. `claude plugin marketplace update gx-design`
3. `claude plugin update gx-design@gx-design`
4. Claude Code 재시작

## 참고 문서

- `디자인-멀티에이전트-팀-구축-가이드.md` — 원본 가이드 정리본 (프로젝트 시작 입력문 템플릿 4종 포함)
- `design-team-스킬-설계안.md` — 설계 근거 (공식 스킬 현황 조사 + mattpocock/skills grilling 패턴 분석)
