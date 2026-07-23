# design-team 스킬 설계안 — 조사 결과 종합

> **작성일**: 2026-07-23
> **목표**: BX·그래픽·UX/UI·영상 디자인 멀티에이전트 팀을 구동하는 **단일 오케스트레이터 스킬** `design-team` 설계.
> **조사 출처**: ① Claude Code 공식 문서(code.claude.com, 2026-07 기준) ② github.com/anthropics/skills ③ github.com/mattpocock/skills
> **관련 문서**: [디자인-멀티에이전트-팀-구축-가이드.md](디자인-멀티에이전트-팀-구축-가이드.md) (원본 가이드 정리본)

---

## 1. 조사 결과 A — 공식 스킬 현황 (요약)

### 1.1 핵심 사실

- 원본 가이드 참고 4의 18개 "공식 스킬" 중 **실제 공식 스킬과 이름이 일치하는 것은 0개**.
- 실존 공식 스킬: **anthropics/skills 저장소 17개** + **Claude Code 내장 12개**.
- 디자인 관련 실존 공식 스킬: `frontend-design`(UI/UX — 현재 환경 설치됨), `canvas-design`(포스터·비주얼), `web-artifacts-builder`(웹 화면), `brand-guidelines`, `algorithmic-art`, `theme-factory`. 그 외 유용: `skill-creator`(스킬 제작), `/batch`(병렬), `/dataviz`(차트).
- **서브에이전트 frontmatter의 `skills:`(스킬 사전 로드)와 `memory:`(user/project/local 크로스세션 메모리)는 공식 지원 확인** — 원본 가이드의 에이전트 명세는 그대로 유효.
- 서브에이전트 공식 frontmatter 키: `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `effort`, `isolation`, `color`, `initialPrompt`.
- SKILL.md 공식 frontmatter 키: `name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`(`fork`), `agent`, `hooks`, `paths`, `shell`. (`description`+`when_to_use` 합산 1,536자 제한)
- 스킬 사전 로드 방식: `skills:`에 나열하면 서브에이전트 시작 시 전체 내용이 컨텍스트에 주입되고, 나열하지 않은 프로젝트/사용자 스킬도 서브에이전트가 Skill 도구로 호출 가능.

### 1.2 18개 이름별 매핑 (원본 가이드 참고 4 → 실체)

| 문서 표기 | 가장 가까운 공식 대응 | 현재 환경의 실제 대응물 | design-team 반영 |
|---|---|---|---|
| task-planning | Plan 모드(내장) | superpowers:writing-plans, prometheus | 스킬 본문의 파이프라인 분해 절차로 내장 |
| review | /code-review(코드 전용) | momus, critic 등(코드/플랜용) | `creative-review` 커스텀 유지 |
| parallel-execution | /batch, Workflow 도구 | superpowers:dispatching-parallel-agents | 스킬 본문의 병렬 위임 규칙으로 내장 |
| project-planning | Plan 모드 | prometheus, ralplan | Project Brief 단계로 내장 |
| web-research | WebSearch/WebFetch + Explore | librarian, gx-research, obsidian:defuddle | researcher가 WebSearch/WebFetch 사용 |
| citation | 없음 | — | `design-research` 스킬의 출처 절차가 담당 |
| summarization | 없음(모델 기본 능력) | — | 불필요 |
| competitive-analysis | 없음 | — | `design-research`의 경쟁사 분석 기준이 담당 |
| brainstorming | 없음 | **superpowers:brainstorming 설치됨** | 전략 콘셉트 발산 시 선택 호출 |
| design-thinking | 없음 | — | `design-strategy` 커스텀이 담당 |
| requirements-analysis | 없음 | **oh-my-claudecode:deep-interview** | ★ 브리프 인터뷰 게이트로 신설(§3) |
| structured-writing | doc-coauthoring(공식) | document-writer, humanize-korean | 출력 형식 템플릿으로 내장 |
| figma | Figma MCP(스킬 아님) | **pencil MCP 설치됨**(.pen 시안 제작) | producer의 UI 시안 도구로 연동 |
| react | **frontend-design(공식·설치됨)** | frontend-design, frontend-engineer | 프로토타입 제작 시 로드 지시 |
| html | web-artifacts-builder(공식) | frontend-design + Artifact | 프로토타입/아티팩트 경로 |
| svg | canvas-design(공식·미설치) | — | 그래픽 작업 시 설치 권장 |
| image-prompting | 없음 | — | `creative-production`의 프롬프트 8요소 규칙 |
| motion-design | 없음 | — | `creative-production`의 영상 항목 |

**시사점**: 원본 가이드의 커스텀 스킬 4개는 "공식이 비운 자리"(경쟁분석·디자인씽킹·이미지 프롬프트·모션·디자인 검수)를 정확히 메우므로 유지 가치가 있다. 제작 단계는 공식 `frontend-design` + pencil MCP 연동으로 문서 명세를 넘어 실제 화면·시안 산출까지 확장 가능하다.

---

## 2. 조사 결과 B — mattpocock/skills의 질문 하네스 ("grilling" 계열)

### 2.1 저장소 개요

- https://github.com/mattpocock/skills — MIT, 6개 버킷 폴더(engineering/productivity/misc/personal/in-progress/deprecated)에 41개 스킬. `npx skills@latest add mattpocock/skills` 또는 Claude Code 플러그인으로 설치 가능.
- 인터뷰 패턴은 단일 스킬이 아니라 **하나의 엔진 + 얇은 래퍼 가족**: `grilling`(엔진, 모델 자동 호출) ← `grill-me`(수동 래퍼), `grill-with-docs`(수동 래퍼 + 도메인 모델링 결합), `batch-grill-me`(실험적 진화형).

### 2.2 엔진 `grilling` — SKILL.md 전문 (본문이 단 4문단)

```markdown
---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

Interview me relentlessly about every aspect of this until we reach a shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing. Asking multiple questions at once is bewildering.

If a *fact* can be found by exploring the environment (filesystem, tools, etc.), look it up rather than asking me. The *decisions*, though, are mine — put each one to me and wait for my answer.

Do not act on it until I confirm we have reached a shared understanding.
```

핵심 메커니즘 4가지:

1. **결정 트리(decision tree)**: 계획을 결정들의 트리로 모델링하고, 결정 간 의존 관계를 하나씩 해소하며 가지를 끝까지 내려간다.
2. **사실 vs 결정 구분**: 환경(파일시스템·도구)에서 찾을 수 있는 *사실*은 직접 조사하고 절대 묻지 않는다. *판단이 필요한 결정*만 사용자에게 묻는다.
3. **추천안 동봉**: 모든 질문에 자신의 추천 답을 함께 제시한다.
4. **명시적 종료 게이트**: 사용자가 "공유된 이해에 도달했다"고 확인하기 전에는 실행하지 않는다.

### 2.3 진화형 `batch-grill-me` — frontier 라운드 모델

> 본문은 원문 인용 조각을 원 순서대로 재구성한 고충실도 버전(바이트 단위 원문 필요 시 저장소 직접 클론 권장).

- 결정들을 **설계 트리(design tree)**로 보고, **frontier** = "선행 결정이 이미 해소되어 지금 물을 수 있는 질문 전부"를 계산한다.
- **라운드 단위 진행**: frontier 전체를 번호 붙여 한 번에 묻고(각 질문에 추천안 동봉), 답을 받으면 트리가 재편되어 frontier가 바깥으로 확장 → 다음 라운드.
- 아직 열려 있는 다른 질문에 의존하는 질문은 이번 라운드가 아니라 **다음 라운드로 미룬다**.
- 환경에서 찾을 사실이 필요하면 서브에이전트를 파견하되 블로킹하지 않는다 — 조사 중인 항목의 하류 질문만 대기.
- **종료 조건 = frontier가 빈 상태**: 모든 가지를 방문했고 암묵적 가정이 남지 않았을 때. 그 후에도 사용자 확인 전에는 실행 금지.

### 2.4 질문 수 상한 없음 — 의도된 설계

저장소의 `.out-of-scope/question-limits.md`가 "질문 개수 상한 추가 요청은 스코프 밖"임을 명문화:

- 그릴링은 의도적으로 open-ended다. 어떤 계획은 질문 3개, 어떤 계획은 50개가 필요하다.
- 세션이 길게 느껴지면 탈출구는 이미 있다: 사용자가 언제든 중단하고 현재 상태를 수용하거나, "정리하고 넘어가"라고 자연어로 조종하면 된다. **수치 제한이 아니라 자연어 조종이 의도된 제어 수단.**
- "질문이 너무 많음"(계획이 실제로 미명세 — 정상 동작)과 "질문이 중복·저가치"(프롬프트 품질 문제)를 혼동하지 말 것 — 후자의 해법은 카운터가 아니라 스킬 프롬프트 개선.

### 2.5 ★ 가장 중요한 발견 — AskUserQuestion을 쓰지 않는다

grilling 계열 어디에도 `AskUserQuestion` 도구, multiSelect, 옵션 버튼 UI가 **등장하지 않는다**. 전부 순수 자연어 프롬프트(채팅 텍스트의 번호 목록)다.

→ 따라서 "**AskUserQuestion으로 모호함이 없을 때까지 묻는 하네스**"는 mattpocock 패턴의 이식이 아니라, **그의 메커니즘(트리·frontier·사실/결정 분리·추천안·무상한) + Claude Code의 구조화 질문 UI를 결합하는 우리의 신규 설계**다. 결합 상성은 매우 좋다: AskUserQuestion이 호출당 최대 4문항을 지원하므로 batch-grill-me의 "라운드당 frontier 일괄 질문"과 자연스럽게 맞아떨어진다(1라운드 = AskUserQuestion 1회 = 최대 4문항, 각 문항 첫 옵션 = "(추천)" 표기 = grilling의 추천안 동봉 규칙).

### 2.6 그 외 채택할 패턴

| 패턴 | 원출처 | design-team 적용 |
|---|---|---|
| **DESIGN-IT-TWICE** | codebase-design/DESIGN-IT-TWICE.md | 전략 단계에서 서브에이전트 3개+를 병렬 스폰, 각기 다른 철학으로 "급진적으로 다른" 콘셉트 생성 → 비교 후 소신 있는 추천("무관심이 아니라 확신을 제시"). 원본 가이드의 "전략적 차이가 있는 3안" 요구와 정확히 일치 |
| **2축 독립 리뷰** | code-review | 검수를 두 독립 축(전략 일치 축 / 완성도 축)의 병렬 서브에이전트로 돌리고 **합치지 않는다** — 한 축이 다른 축을 가리지 못하게. `creative-review` 실행 방식으로 채택 |
| **prototype** | prototype/UI.md | "프로토타입은 질문에 답하는 일회용 코드" — URL 파라미터로 토글되는 복수 UI 변형. producer의 프로토타입 제작 규칙으로 채택 |
| **라우터 스킬** | ask-matt | 스킬이 늘어나면 "언제 뭘 쓰는지" 안내 라우터 추가 고려(당장은 불필요) |
| **wayfinder** | engineering/wayfinder | 세션 하나에 안 담기는 대형 디자인 프로젝트를 이슈 트래커의 "결정 티켓 지도"로 관리. 향후 확장 옵션(전문 확보됨, 필요 시 요청) |
| **to-questionnaire** | in-progress | 결정권자가 사용자가 아니라 외부인(클라이언트 등)일 때 비동기 설문 md 생성. 향후 확장 옵션 |

### 2.7 스킬 작성 규율 (writing-great-skills — design-team 제작 시 적용)

- **예측 가능성(Predictability)이 단일 근본 가치**: 매 실행 같은 프로세스를 밟게 하라(같은 출력이 아니라).
- **컨텍스트 부하 vs 인지 부하**: 모델 자동 호출 스킬의 description은 매 턴 컨텍스트 비용, 수동 호출 스킬은 사용자 기억 비용. 분리/병합 결정마다 어느 예산을 쓸지 선택.
- **정보 위계**: 본문 절차(1차) > 본문 참조(2차) > 별도 파일로 점진 공개(3차). 링크는 **문구가 강해야 실제로 따라간다**("필수 대상 뒤에 약한 문구의 포인터 = 편차 버그").
- **실패 모드 분류와 치료**: Premature Completion(완료 기준을 검증 가능하게), Duplication, Sediment(퇴적된 낡은 지시), Sprawl(장황), **No-Op**("모델이 원래 하는 걸 지시 — 부하만 내고 아무것도 안 함"), **Negation**("코끼리를 생각하지 마" — 금지 대신 긍정형으로 지시).
- 참고: Matt의 `disable-model-invocation`은 Claude Code에선 **공식 지원 키**다(§1.1). 그가 최소 2필드 스펙 + 자체 툴링을 병행하는 건 Codex 등 타 하네스 호환 때문(모든 스킬에 `agents/openai.yaml` 동봉).
- grilling 본문이 4문단에 불과하듯, **SKILL.md는 짧게** 유지하고 상세 절차는 참조 파일로 분리한다.

---

## 3. design-team 스킬 설계안

### 3.1 아키텍처 옵션

**옵션 A — 오케스트레이터 스킬 + 에이전트 파일 3개 (원본 가이드 확장, 추천)**

```text
.claude/
├── agents/
│   ├── design-researcher.md      # haiku, skills: design-research, memory: project
│   ├── design-strategist.md      # sonnet, skills: design-strategy, memory: project
│   └── creative-producer.md      # sonnet, skills: creative-production·creative-review, memory: project
└── skills/
    ├── design-team/              # ★ 신설 — 오케스트레이터 진입점
    │   ├── SKILL.md              # 짧은 본문: 5단계 파이프라인 + 게이트 규칙
    │   ├── BRIEF-INTERVIEW.md    # 0단계: AskUserQuestion 그릴링 게이트 상세
    │   ├── DESIGN-IT-TWICE.md    # 전략 N안 병렬 생성·비교 절차
    │   └── REVIEW-AXES.md        # 2축 독립 검수 실행 절차
    ├── design-research/SKILL.md      # (가이드 원안 유지)
    ├── design-strategy/SKILL.md      # (가이드 원안 유지)
    ├── creative-production/SKILL.md  # (가이드 원안 유지)
    └── creative-review/SKILL.md      # (가이드 원안 유지)
outputs/
├── brief/        # ★ 신설 — 인터뷰 산출 브리프
├── research/ strategy/ production/ final/
```

- 근거: `skills:`/`memory:` 공식 지원이 확인되어 가이드 원안이 유효하고, 빠져 있던 조각이 정확히 "진입점 오케스트레이터 + 모호함 제거 게이트"다. 에이전트별 크로스세션 메모리(프로젝트 축적 학습)와 자동 위임도 살릴 수 있다.

**옵션 B — 완전 단일 스킬 (에이전트 파일 없음)**

- design-team 스킬 참조 파일(ROLES.md)에 3개 역할 프롬프트를 넣고, Agent 도구로 범용 서브에이전트를 즉석 스폰(호출 시 model: haiku/sonnet 지정).
- 장점: 설치물이 스킬 폴더 하나 — 이식성 최상. 단점: 에이전트별 `memory:` 크로스세션 학습 불가, 자동 위임 불가.

어느 쪽이든 **플러그인 패키징**(skills/ + agents/ + plugin.json)으로 승격 가능 — 옵션 A가 플러그인 표준 구조와 그대로 합동된다.

### 3.2 SKILL.md 스켈레톤 (옵션 A 기준 초안)

```markdown
---
name: design-team
description: BX·그래픽·UX/UI·영상 디자인 프로젝트의 멀티에이전트 워크플로 실행. 디자인 기획·제작 요청이 오면 사용한다. 브리프 인터뷰로 모호함을 제거한 뒤 Research → Strategy → Production → Review를 서브에이전트로 지휘한다.
argument-hint: "[프로젝트 한 줄 설명]"
---

# Design Team Orchestrator

당신은 이 프로젝트의 AI Creative Director다. 아래 5단계를 순서대로 진행한다.
각 단계의 완료 기준을 충족했을 때만 다음 단계로 간다.

## 0. 브리프 인터뷰 — 게이트
[BRIEF-INTERVIEW.md](BRIEF-INTERVIEW.md)를 읽고 그 절차를 그대로 수행한다.
결정 트리의 frontier가 비고 사용자가 브리프를 승인하기 전에는
어떤 리서치도 제작도 시작하지 않는다.
산출물: outputs/brief/YYYY-MM-DD_<project>_brief.md

## 1. Research
승인된 브리프를 근거로 design-researcher에게 위임한다.
독립적인 조사 축(시장/경쟁사/사용자/트렌드)은 병렬로 스폰한다.
위임 시 브리프 경로·저장 경로·완료 기준을 명시한다(전달 11항목 규칙).

## 2. Strategy
[DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md) 절차로 design-strategist를 병렬 스폰해
전략적으로 다른 콘셉트 3안을 만들고, 비교표와 함께 소신 있는 추천 1안을 정한 뒤
AskUserQuestion(옵션별 preview에 콘셉트 요약)으로 사용자 선택을 받는다.
핵심 전략은 사용자 승인 없이 확정하지 않는다.

## 3. Production
선택된 전략을 creative-producer에게 위임한다.
UI 프로토타입이 필요하면 frontend-design 스킬을, .pen 시안이 필요하면 pencil MCP를 쓰게 한다.

## 4. Review
[REVIEW-AXES.md](REVIEW-AXES.md) 절차로 전략 일치 축과 완성도 축을
독립 병렬 검수하고, Critical이 있으면 해당 단계 에이전트에 수정을 위임한다.
통과본을 outputs/final/에 저장하고 결과를 보고한다.
```

### 3.3 BRIEF-INTERVIEW.md 명세 (grilling × AskUserQuestion 결합 — 신규 설계)

1. **결정 트리 구축**: 요청을 읽고 결정 노드를 도출한다 — 매체 유형(BX/그래픽/UX·UI/영상/복합), 목표, 타깃, 핵심 문제, 필요 산출물, 필수 요구/제약, 레퍼런스, 톤, 성공 기준, 저장 규칙 등. 노드 간 의존 관계를 표시한다(예: "산출물 범위"는 "매체 유형"에 의존).
2. **사실/결정 분리**: 프로젝트 파일·outputs/·웹에서 확인 가능한 *사실*은 직접 조사한다 — 사용자에게 묻지 않는다. *판단이 필요한 결정*만 질문한다.
3. **frontier 계산**: 선행 결정이 모두 해소된 질문만 이번 라운드에 올린다. 미해소 결정에 의존하는 질문은 다음 라운드로 미룬다.
4. **라운드 실행**: AskUserQuestion 1회 = 최대 4문항. 각 문항은 옵션 2~4개 + 자동 "Other". **첫 옵션 = 추천안, 라벨에 "(추천)" 표기**, description에 추천 근거를 쓴다. 배타적이지 않은 선택지는 multiSelect를 켠다.
5. **트리 갱신**: 답변으로 트리를 재구성하고 새 frontier를 계산해 다음 라운드로. 질문 수 상한은 두지 않는다(§2.4의 정책 계승).
6. **탈출구**: 사용자가 "그만, 진행해"라고 하면 즉시 인터뷰를 종료하되, 미해소 결정은 브리프에 **[가정]** 표기로 명시하고 합리적 기본값을 채워 진행한다(원본 가이드의 "합리적 가정 명시 후 진행" 원칙과 결합).
7. **종료 게이트**: frontier가 비면 브리프 전문(프로젝트명/유형/배경/목표/타깃/문제/산출물/요구/제약/참고자료/성공 기준/[가정] 목록)을 제시하고 최종 승인 질문 1건을 올린다. **승인 후에만** 파이프라인을 시작하고 브리프를 outputs/brief/에 저장한다.

### 3.4 제작 방법 (스킬을 잘 만들기 위한 스킬 조합)

1. **`superpowers:writing-skills` 로드** — 작성 규율·구조·배포 전 검증 절차 (스킬 생성 작업의 필수 선행).
2. **공식 `skill-creator` 방법론 반영** — 본문 짧게, 상세는 참조 파일로 점진 공개, description 작성 요령.
3. **mattpocock `writing-great-skills` 점검표 적용** — No-Op/Negation/Sprawl/Sediment/Premature Completion 검사, 완료 기준의 검증 가능성, 링크 문구 강도.

### 3.5 확정 사항 (2026-07-23 사용자 결정)

| # | 결정 | 확정 |
|---|---|---|
| 1 | 팀원 형태 | **A. 에이전트 파일 3개 + 오케스트레이터 스킬** |
| 2 | 인터뷰 방식 | **라운드 배치(frontier 전체)** — 상한 숫자 없이 그 라운드에 물을 수 있는 질문 전부(AskUserQuestion 상한에 맞춰 4문항씩 분할 연속 호출). 최초 "최대 5문항" 결정을 2026-07-23 사용자 재결정으로 frontier 전체로 변경 |
| 3 | 설치 범위 | **처음부터 플러그인 구조** — 플러그인명 `gx-design`(최초 sq-design에서 개명), D:\SQ\design-plugin 루트에 .claude-plugin/ + skills/ + agents/ 구성 |

---

## 4. 구축 및 검증 결과 (2026-07-23)

- **구축**: 플러그인 13파일 + README + outputs 5폴더 생성 완료. superpowers:writing-skills(TDD for skills) 규율로 제작.
- **RED(베이스라인, 스킬 없음)**: 모호한 요청("대학생 커피 원두 구독, 브랜드랑 앱 디자인해줘")에 대해 ① 상류 결정(목표·타깃·문제) 건너뛰고 스타일 3안부터 질문 ② 1라운드 후 제작 돌입 ③ 화면 목록 스코프 발명 ④ "알아서 정해도 진행" 셀프 권유 ⑤ 리서치 단계 부재 — 5개 실패 관찰.
- **GREEN(스킬 로드)**: 같은 요청에서 ① 사실 수집(프로젝트 파일 확인) 선행 ② 1라운드 질문 4개가 전부 상류·중류 결정(프로젝트 단계/핵심 문제/타깃 세그먼트/네이밍 여부) ③ 각 문항 첫 옵션 "(추천)" + 근거 ④ 스타일·화면 목록·디자인 산출물 미제시 ⑤ 셀프 탈출구 권유 없음 ⑥ 다음 라운드 예고(산출물 범위·제약) — 5개 실패 전부 해소 확인.
- **구조 검증**: JSON 매니페스트 2건 유효, frontmatter 8건 유효, name 중복 없음, `skills:` 참조 4건 전부 대응 SKILL.md 존재, tools 전부 유효, memory 값 유효, design-team 참조 파일 3건 존재 — ALL PASS.
- **테스트 깊이 한계(잔여 부채)**: RED/GREEN 각 1회 실행. writing-skills가 권장하는 5회+ 반복과 압박 시나리오(시간 압박·매몰 비용 결합)는 미실시 — 실제 프로젝트 첫 실행이 REFACTOR 입력이 된다.
- **설치 후 확인 필요**: 재시작 후 에이전트·스킬 등록 여부, 플러그인 컨텍스트에서 `skills:` 사전 로드가 접두사 없이 해석되는지(대비책으로 에이전트 본문에 Skill 도구 로드 가드 1줄 포함).

---

## 5. v0.2 확장 — 커맨드 개편 + gx-redesign (2026-07-23)

- **커맨드 체계**: design-team → `gx-design`(신규 제작, 5단계), 신설 `gx-redesign`(기존 개선, 진단 선행 6단계: 자산 인벤토리+개선 브리프 → 진단 Audit → 갭 리서치(조건부) → 개선 강도 전략 3안(최소 개입/리프레시/리뉴얼) → before/after 제작 → 3축 검수). 방법론 스킬 4종은 oh-my-gx:gx-research와의 이름 충돌을 피해 이름 유지.
- **gx-redesign TDD**: RED(스킬 없음)에서 4개 실패 관찰 — 진단 부재, 상류 질문 누락("요즘 느낌"→레퍼런스 취향 직행), 게이트 없음, before/after 부재 → GREEN(스킬 로드)에서 4개 전부 해소 확인 — 자산 인벤토리 표 + before 기준선 태깅, "요즘 느낌" 상류 분해(계기/성공 기준/범위/낡음의 정체), 라운드 구조 예고, 승인 전 제안 금지 선언.
- **자산 파악 보강(v0.2.1)**: 자산 유형별 파악 방법(문서 Read / .pen pencil / 코드 실행 / 이미지 시각 분석 / 배포 화면 브라우저 캡처) 명시 + 자산 부재 시 첫 라운드에서 자료 요청(스크린샷/URL/파일 경로/Figma 링크) 규칙 추가.
- **배포**: GitHub github.com/bs-koo/gx-design (main). 원격 설치: `/plugin marketplace add bs-koo/gx-design` → `/plugin install gx-design@gx-design`.

## 6. v0.3 확장 — 실물 제작 게이트 (2026-07-23)

- **배경**: 첫 실전 실행(플러그인 소개 10초 Reels)에서 파이프라인이 md 명세로 끝나자 사용자가 "영상이 아니라 md를 만들어준 것이냐"고 지적 → Remotion으로 실제 MP4를 제작해 해소. 이 경험을 파이프라인에 제도화.
- **신설**: `skills/gx-design/PRODUCTION-HANDOFF.md` — 검수 통과 보고 직후 실물 제작 여부·방식을 AskUserQuestion(multiSelect)으로 묻는 게이트. gx-design 단계 5 / gx-redesign 단계 6으로 편입(참조 공유).
- **경로 4종**: A 코드 렌더링(Remotion·FFmpeg·HTML→MP4/PNG, 스틸 선검증, [가정] 표기) / B Gemini 프롬프트 패키지 / C 편집 도구 핸드오프(브리프의 도구 기준) / D 문서로 종료. 결과물이 문서 자체면 게이트 생략+보고.
- **Gemini 필수 정책**: 주 사용자층(개발자·사업부)이 생성 도구로 Gemini를 주로 쓰므로 **영상·이미지 유형의 선택지에 Gemini 옵션을 반드시 포함**. 패키지 구조(사용법/공통 스타일 블록/클립별 PROMPT+한국어 해설/합본 가이드/검수 체크리스트)와 원칙(온스크린 텍스트는 후편집으로 분리 — 생성 모델의 한글 렌더링 불안정, 클립당 ~8초 분할, 모델 버전 비의존 서술형, 영어 본문 기본) 명시.
- **추천 배치 기준**: UI·터미널·타이포·도형 중심 → 코드 렌더링 추천(텍스트 정확도 100%) / 실사·인물·일러스트 중심 → Gemini 추천(코드 재현 불가).
