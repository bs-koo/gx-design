<div align="center">

# gx-design

**모호함이 0이 되면, 디자인 팀이 움직입니다.**

BX · 그래픽 · UX/UI · 영상 — 한 줄로 요청하세요.
AI 크리에이티브 디렉터가 결정 트리가 빌 때까지 인터뷰하고,
리서치 → 전략 → 제작 → 검수 → 실물 제작 파이프라인을 전문 에이전트 팀으로 지휘합니다.

[빠른 시작](#빠른-시작) • [왜 gx-design인가?](#왜-gx-design인가) • [어떻게 작동하나?](#어떻게-작동하나) • [구성](#구성) • [FAQ](#faq)

</div>

---

## 빠른 시작

```
/plugin marketplace add bs-koo/gx-design
/plugin install gx-design@gx-design
```

Claude Code를 재시작한 뒤, 만들고 싶은 것을 한 줄로 말하면 됩니다.

```
/gx-design:gx-design 대학생 캠퍼스 중고거래 서비스 UX/UI
/gx-design:gx-redesign 커머스 앱 홈·상세 화면 리뉴얼
```

슬래시 커맨드 없이 자연어로 "○○ 브랜드 만들어줘", "○○ 화면 리뉴얼하고 싶어"라고 해도 신규 제작/기존 개선을 판별해 해당 워크플로가 자동으로 시작됩니다.

## 왜 gx-design인가?

**1. 묻지 않고 만든 디자인은 근거가 없습니다.**

AI에게 디자인을 맡기면 대개 질문 한두 개 뒤에 그럴듯한 시안이 나옵니다 — 목표도, 타깃도, 성공 기준도 정해지지 않았는데요. gx-design은 반대로 갑니다. 요청을 결정 트리로 펼치고, 지금 답할 수 있는 질문(frontier)을 라운드로 물어서, 모호함이 구조적으로 소진된 뒤에만 작업을 시작합니다.

**2. 매체가 달라도 일은 같은 순서로 흐릅니다.**

BX든 화면이든 영상이든 실무는 Research → Strategy → Production 순서를 따릅니다. 그래서 에이전트를 매체별이 아니라 **업무 단계별**로 나눴습니다. 한 팀이 네 매체를 전부 감당하고, 어떤 프로젝트에서도 재사용됩니다.

**3. 예쁜 것과 맞는 것은 다릅니다.**

결과물은 전략 일치 축과 완성도 축, 두 독립 검수자가 병렬로 봅니다. 두 보고는 합치지 않습니다 — 한 축의 호평이 다른 축의 결함을 가리지 못하게 하기 위해서입니다.

## 어떻게 작동하나?

### `/gx-design:gx-design` — 신규 제작 (6단계)

```
요청 한 줄
 → 0. 브리프 인터뷰    결정 트리 frontier 라운드 — 승인 전에는 어떤 산출물도 만들지 않음
 → 1. 리서치           시장 / 경쟁사 / 사용자 / 트렌드 병렬 조사
 → 2. 전략 3안         본질 우선 / 차별화 우선 / 시스템 우선 — 철학이 다른 3안 병렬 개발 후 선택
 → 3. 제작             명세 · 카피 · 생성형 AI 프롬프트 · 프로토타입
 → 4. 검수             전략 일치 축 + 완성도 축 독립 병렬 → outputs/final/
 → 5. 실물 제작(선택)  코드 렌더링(실제 MP4·PNG) / Gemini 프롬프트 / 편집 도구 핸드오프 중 선택
```

### `/gx-design:gx-redesign` — 기존 개선 (7단계)

```
요청 한 줄
 → 0. 자산 인벤토리 + 개선 브리프    기존 문서·.pen·코드·이미지·배포 화면 전수 파악 후 인터뷰
 → 1. 진단(Audit)                   "낡았다"는 인상을 Critical/Major/Minor 문제 목록으로 번역
 → 2. 갭 리서치 (조건부)             경쟁·트렌드 대비 격차 분석
 → 3. 개선 강도 3안                  최소 개입 / 리프레시 / 리뉴얼 중 선택
 → 4. 제작                          모든 변경을 before → after → 근거 3열로 기록
 → 5. 검수                          2축 + 개선 목표 달성 축 = 3축 병렬
 → 6. 실물 제작(선택)                신규 제작과 동일한 게이트 — after 실물까지
```

### 브리프 인터뷰는 이렇게 묻습니다

- 파일·웹에서 확인 가능한 **사실은 직접 조사하고, 판단이 필요한 결정만** 질문합니다.
- 선택지 UI로 묻고, 각 문항의 첫 옵션은 근거가 붙은 **추천안**입니다.
- 상류(목표·타깃·문제)가 정해지기 전에 하류(스타일·레퍼런스)를 묻지 않습니다.
- 질문 총량 제한은 없습니다. 지겨우면 **"그만, 진행해"** — 남은 결정은 [가정]으로 표기하고 진행합니다.
- 사용자 승인이 필요한 지점은 **브리프 승인**과 **전략 선택** 두 곳입니다.

## 구성

| 종류 | 이름 | 역할 |
|---|---|---|
| 스킬 | `gx-design` | 신규 디자인 진입점: 브리프 인터뷰 게이트 + 5단계 파이프라인 지휘 |
| 스킬 | `gx-redesign` | 기존 디자인 개선 진입점: 자산 인벤토리 → 진단(Audit) → 개선 파이프라인 지휘 |
| 스킬 | `design-research` | 리서치 방법론 (researcher에 사전 로드) |
| 스킬 | `design-strategy` | 전략 방법론 (strategist에 사전 로드) |
| 스킬 | `creative-production` | 제작 방법론 (producer에 사전 로드) |
| 스킬 | `creative-review` | 검수 기준 (producer 사전 로드 + 검수 축에 사용) |
| 에이전트 | `design-researcher` (haiku) | 시장·사용자·경쟁사·트렌드 조사 → outputs/research/ |
| 에이전트 | `design-strategist` (sonnet) | 전략·콘셉트 수립 → outputs/strategy/ |
| 에이전트 | `creative-producer` (sonnet) | 명세·카피·프롬프트·프로토타입 제작 → outputs/production/ |

상세 절차는 참조 파일로 분리되어 있습니다:
`gx-design/` — BRIEF-INTERVIEW.md(인터뷰 게이트) · DESIGN-IT-TWICE.md(전략 3안 병렬) · REVIEW-AXES.md(2·3축 독립 검수) · PRODUCTION-HANDOFF.md(실물 제작 게이트)
`gx-redesign/` — REDESIGN-INTERVIEW.md(자산 인벤토리 + 개선 인터뷰)

- 산출물: 실행한 프로젝트의 `outputs/brief|research|strategy|production|final/` (저장 시 자동 생성)
- 파일명 규칙: `YYYY-MM-DD_<project>_<document-type>.md`
- 상시 토큰 비용: 세션당 약 795 tok — 상세 절차는 호출 시에만 로드됩니다.

## 사용 예시

```
/gx-design:gx-design 혼자 사는 대학생 대상 요리 커뮤니티 서비스 BX
/gx-design:gx-design 신제품 런칭 캠페인 키 비주얼과 SNS 그래픽
/gx-design:gx-design 서비스 소개 30초 Instagram Reels 영상
/gx-design:gx-redesign 사내 그룹웨어 대시보드 UX 리뉴얼
```

## 설치 확인

재시작 후 아래를 입력해 등록 상태를 검증할 수 있습니다.

```
현재 등록된 디자인 서브에이전트(design-researcher, design-strategist, creative-producer)와
스킬(gx-design, gx-redesign, design-research, design-strategy, creative-production, creative-review)을
역할·모델·도구·사전 로드 스킬 표로 확인해줘. 로드되지 않은 항목이 있으면 원인을 분석해줘.
```

## FAQ

**Q. 결과가 md 명세로만 나오나요? 실제 영상·이미지 파일은요?**
검수 통과 직후 실물 제작 게이트가 열립니다 — 코드 렌더링(Remotion·HTML로 실제 MP4/PNG 생성), Gemini 프롬프트 패키지(Gemini에 복붙해 생성하도록 클립별 프롬프트 + 자막 후편집 지시 제공), 편집 도구 체크리스트 중에서 선택합니다. 영상·이미지 프로젝트의 선택지에는 Gemini가 항상 포함됩니다.

**Q. 질문이 너무 많이 나오면 어떻게 하나요?**
"그만, 진행해"라고 하면 즉시 인터뷰가 끝납니다. 미확정 결정은 합리적 기본값이 채워지고 브리프에 [가정]으로 표기됩니다. 질문 수 상한을 두지 않는 것은 의도된 설계입니다 — 어떤 프로젝트는 3개, 어떤 프로젝트는 20개가 필요하고, 제어 수단은 숫자가 아니라 사용자의 한마디입니다.

**Q. 디자인이 Figma나 모바일 앱에만 있으면 리디자인은 어떻게 하나요?**
로컬에 자산이 없으면 첫 라운드에서 자료를 요청합니다 — 화면 스크린샷(이미지를 직접 시각 분석), 서비스 URL(브라우저로 접속·캡처), 디자인 파일 경로 중 제공 가능한 것을 물어봅니다. 기억에 의한 묘사만으로 진단하지 않습니다.

**Q. 리서치는 건너뛰고 화면 명세만 받고 싶은데요.**
단계 축소를 요청하면 오케스트레이터가 축소안을 제안하고, 승인 후 그 범위로 진행합니다. 단계를 말없이 건너뛰지 않는 것이 원칙입니다.

**Q. `design-research` 같은 스킬은 직접 호출하는 건가요?**
아니요, 내부 부품입니다. 각 에이전트에 사전 로드되는 방법론이라 직접 호출할 일은 없습니다. 입구는 `gx-design`과 `gx-redesign` 두 개뿐입니다.

## 수정·릴리즈 워크플로 (개발자용)

플러그인은 **버전별로 캐시에 복사 설치**되므로, 파일만 수정하면 설치본에 반영되지 않습니다.

로컬 개발 설치:

```
/plugin marketplace add D:\SQ\design-plugin
/plugin install gx-design@gx-design
```

수정 반영:

1. `.claude-plugin/plugin.json`의 `version`을 올린다 (예: 0.2.1 → 0.2.2)
2. `claude plugin marketplace update gx-design`
3. `claude plugin update gx-design@gx-design`
4. Claude Code 재시작

릴리즈 (main 직접 커밋은 훅이 차단하므로, 변경은 작업 브랜치에서 커밋 후 main에 병합):

1. `claude plugin tag .` — `gx-design--v{version}` 태그 생성 (매니페스트 정합성 검증 포함)
2. `git push origin main --tags`
3. `gh release create gx-design--v{version}`

## 요구사항

- Claude Code 최신 버전 (서브에이전트 frontmatter `skills:` / `memory:` 지원 버전)
- 선택 연동 — 있으면 더 강해집니다:
  - pencil MCP: .pen 디자인 파일 열람·시안 제작
  - Playwright MCP: 배포 화면 캡처, 프로토타입 실행 확인
  - frontend-design 스킬(공식): UI 프로토타입 품질

## 참고 문서

- `디자인-멀티에이전트-팀-구축-가이드.md` — 원본 가이드 정리본 (프로젝트 시작 입력문 템플릿 4종 포함)
- `design-team-스킬-설계안.md` — 설계 근거 (공식 스킬 현황 조사 + mattpocock/skills grilling 패턴 분석 + TDD 검증 기록)
