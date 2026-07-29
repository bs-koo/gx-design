# MengTo/Skills 디자인 규칙 흡수 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** MengTo/Skills(MIT)의 Gemini·전략 파이프라인 적합 규칙만 규칙 재서술로 흡수 — 레퍼런스 기반 생성(신규 REFERENCE-DRIVEN.md) + 안티-슬롭 어휘·variants>rerolls·수용 체크(기존 파일 보강).

**Architecture:** 신규 참조 파일 1개(`skills/gx-design/REFERENCE-DRIVEN.md`)에 레퍼런스 기반 생성 규칙을 중앙화하고, 나머지 고가치 규칙은 기존 규칙 파일(VISUAL-CRAFT·PROMPT-PLAYBOOK·creative-production·creative-review)에 외과적으로 흡수한다. 교차 참조는 상대경로 마크다운 링크로 연결한다. 외부 스킬 런타임 의존 없음.

**Tech Stack:** 마크다운 스킬 파일 + Claude Code 플러그인 매니페스트(`.claude-plugin/`). 빌드·테스트 프레임워크 없음 — 검증은 내용/상호참조 grep + JSON 정합성 확인 + 리뷰 서브에이전트.

## Global Constraints

모든 태스크에 암묵 적용:
- 버전 `0.6.0` → `0.7.0` (minor).
- 흡수는 **규칙 재서술** — MIT 원문 문장 복붙 금지. 스켈레톤·다이얼은 필드 구성만 참고, 문구는 한국어·Gemini 맥락으로 새로 씀.
- `REFERENCE-DRIVEN.md`는 얇게 유지(목표 40~55줄).
- 디자인 톤 기준이 있으면 **톤 기준이 상위** — 근접도·visual DNA는 그 안에서 정함.
- 기존 파일 문체 유지(한국어, 간결, 번호 섹션). 커밋은 브랜치 `feat/absorb-mengto-rules`.
- 커밋 트레일러: `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.

---

### Task 1: 신규 REFERENCE-DRIVEN.md 작성

**Files:**
- Create: `skills/gx-design/REFERENCE-DRIVEN.md`

**Interfaces:**
- Produces: 파일 경로 `skills/gx-design/REFERENCE-DRIVEN.md`, 앵커 섹션 `§4 저작권 안전 가드레일`, `§6 검수 연계`. Task 3(PROMPT-PLAYBOOK 링크)·Task 4(수용 체크의 저작권 가드 참조)·Task 5(단계 3 배달)가 이 경로와 §번호에 의존.

- [ ] **Step 1: 파일 생성**

아래 내용으로 `skills/gx-design/REFERENCE-DRIVEN.md`를 만든다:

```markdown
# REFERENCE-DRIVEN — 레퍼런스 구동 생성 규격

레퍼런스 이미지·영상을 *입력*으로 써서 생성할 때(Gemini 이미지 입력·스타일 트랜스퍼, 1레퍼런스→N브랜드 확장) 이 규격을 [PROMPT-PLAYBOOK.md](PROMPT-PLAYBOOK.md)와 함께 적용한다.
근거: MengTo/Skills(MIT)의 레퍼런스 기반 브랜드 월드 생성 규칙을 우리 규격으로 흡수한 것이다(원문 복제 아님·규칙 재서술).

**톤 기준과의 구분**: 디자인 톤 기준([DESIGN-TONE-ANCHOR.md](DESIGN-TONE-ANCHOR.md)) = 자기 브랜드 = 재현할 구속. 레퍼런스 = 타인 자산 = 재현 금지(§4 저작권 가드 대상). 톤 기준이 있으면 그것이 상위다 — 근접도·visual DNA는 톤 기준 안에서 정한다.

## 1. 레퍼런스 라벨링

- 입력 레퍼런스마다 역할을 문장으로 고정한다: "Image A = 시각 언어 레퍼런스, Image B = 현재 콘셉트 앵커." (PROMPT-PLAYBOOK §2.5 연장)
- 레퍼런스가 없으면 지어내지 않는다 — 파일·URL을 요청한다.

## 2. 근접도 다이얼 (similarity dial)

- 레퍼런스에 얼마나 가깝게 갈지를 30 / 50 / 70 / 85%로 명시한다. **측정 점수가 아니라 의도 전달용**이다.
- 기본값 70(인접 브랜드 패밀리 느낌). 30~50은 느슨한 영감, 85는 매우 근접하되 §4 보호 시그니처는 여전히 재현 금지 — 대신 시그니처 요소 4개 이상을 의도적으로 다르게 한다.
- 근접도 다이얼은 VISUAL-CRAFT 톤 다이얼(VARIANCE/MOTION/DENSITY)의 형제다 — 승인된 전략에 종속된 실행 보조로만 쓰고 전략을 대체하지 않는다.

## 3. visual DNA 2-리스트

레퍼런스를 두 리스트로 분해해 프롬프트에 반영한다:
- **재사용 문법(빌릴 것)**: 밀도, 팔레트 관계, 표면 질감, 타입 스케일, 여백 리듬 — 원리로 서술한다.
- **보호 시그니처(빌리지 않을 것)**: 정확한 인물·마스코트·구도·모티프, 그리고 브랜드명·워드마크 letterform. §4로 넘긴다.

## 4. 저작권 안전 가드레일 (필수)

- 워드마크·로고 letterform·유명 캐릭터/로고를 **정확히 재현하지 않는다** — 원리(비례·리듬·무드)만 추상화해 가져온다. "inspired, not copying".
- 근접도 85를 요청해도 보호 시그니처는 재현하지 않는다. 재현 금지 대상은 프롬프트에 긍정 서술로 잠근다(PROMPT-PLAYBOOK §2.4): "an original wordmark, not resembling any existing brand's letterforms".
- 이 가드는 안티-슬롭(VISUAL-CRAFT §1)과 다른 축이다 — 안티-슬롭 = 흔함 회피, 저작권 가드 = 타인 자산 재현 회피.

## 5. brand matrix / prompt spine (1레퍼런스 → N브랜드일 때만)

- 공통 상수 4~6개(그리드·팔레트 관계·표면·타입 스케일)를 prompt spine 하나로 고정한다.
- 브랜드별로 이름·의미·환경·모티프만 변주해 브랜드당 프롬프트 1개를 만든다(변형은 PROMPT-PLAYBOOK "변형 > 재롤" 규율을 따른다).
- 검증: 워드마크 재현 0건 / 각 브랜드가 보호 시그니처에서 4개 이상 다름.

## 6. 검수 연계

검수 축 A(전략 일치, [REVIEW-AXES.md](REVIEW-AXES.md))에 두 항을 추가 점검한다:
- 산출물의 레퍼런스 근접도가 요청한 다이얼값과 맞는가.
- §4 저작권 가드 위반 0건인가(워드마크·letterform·유명 시그니처 재현 없음).
```

- [ ] **Step 2: 검증 — 파일·섹션·분량**

Run: `grep -nE '^## [0-9]' skills/gx-design/REFERENCE-DRIVEN.md && wc -l < skills/gx-design/REFERENCE-DRIVEN.md`
Expected: §1~§6 여섯 섹션이 모두 출력되고, 줄 수가 40~55 범위. `§4 저작권 안전 가드레일`·`§6 검수 연계` 존재. 원문 영어 문장 복붙 없음(한국어 재서술).

- [ ] **Step 3: 커밋**

```bash
git add skills/gx-design/REFERENCE-DRIVEN.md
git commit -m "feat: 레퍼런스 구동 생성 규격 신설(REFERENCE-DRIVEN) — 근접도 다이얼·visual DNA·저작권 가드

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: VISUAL-CRAFT.md §1·§2 보강 (안티-슬롭 어휘)

**Files:**
- Modify: `skills/gx-design/VISUAL-CRAFT.md` (§1 안티-슬롭 캘리브레이션, §2 톤 다이얼)

**Interfaces:**
- Consumes: 없음(독립).
- Produces: §1에 "명명된 룩 슬롭 워치리스트"·"부정 정의", §2에 "룩별 다이얼" — 다른 태스크가 직접 참조하진 않음(어휘 보강).

- [ ] **Step 1: §1 끝(3대 기본 룩 불릿 뒤)에 두 문단 추가**

`## 1. 안티-슬롭 캘리브레이션` 섹션의 마지막 불릿("자유로운 축은 위 기본값이 아니라…") 뒤에 추가:

```markdown

**명명된 룩 슬롭 워치리스트** — 위 3대 룩 외에도, 커뮤니티가 "기본으로 예쁜 것"으로 수렴시키는 룩이 새 디폴트 슬롭이 된다: dark-glass-clean, mesh-gradient-dark-blue, clean-minimal-beige, editorial-tech, solar-duotone, high-contrast-skeuomorphic. 이름에 *clean·glass·dark·tech* 가 반복되면 경계 신호다 — 브리프가 지정하지 않는 한 자유 축을 이 룩으로 채우지 않는다.

**부정 정의로 룩 못박기 ("not X, not Y")** — 의도한 룩을 서술할 때 가장 가까운 흔한 클리셰 2개와 대비해 정의한다: "frosted depth가 있는 glass — pastel glassmorphism도 sci-fi 패널도 아님." 이 한 줄이 슬롭 회피를 프롬프트·명세에 고정한다.
```

- [ ] **Step 2: §2 끝(3다이얼 불릿 뒤, "다이얼은 승인된 전략에…" 문장 앞)에 한 줄 추가**

`## 2. 톤 다이얼` 섹션의 세 다이얼 불릿 바로 뒤에 추가:

```markdown
- 특정 룩을 택하면 그 룩 전용 다이얼(예: glass intensity, mesh visibility, frame visibility, accent restraint)을 위 3다이얼에 덧붙여 명세에 함께 적는다.
```

- [ ] **Step 3: 검증**

Run: `grep -nE '슬롭 워치리스트|not X, not Y|룩 전용 다이얼' skills/gx-design/VISUAL-CRAFT.md`
Expected: 세 패턴 모두 매치. §1·§2 구조 유지, 기존 문단 훼손 없음.

- [ ] **Step 4: 커밋**

```bash
git add skills/gx-design/VISUAL-CRAFT.md
git commit -m "feat: VISUAL-CRAFT 안티-슬롭 보강 — 명명된 룩 워치리스트·부정 정의·룩별 다이얼

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: PROMPT-PLAYBOOK.md 보강 (반복 규율·constraints 카드·2-pass·링크)

**Files:**
- Modify: `skills/gx-design/PROMPT-PLAYBOOK.md` (§2.3, §2.5, 신규 §2.7, §4)

**Interfaces:**
- Consumes: Task 1의 `REFERENCE-DRIVEN.md` 경로(§2.5 링크 대상). Task 1 완료 후 실행.
- Produces: §2.7 "변형 > 재롤" — Task 1 §5가 이 규율을 이름으로 참조.

- [ ] **Step 1: §2.3(시리즈 일관성 문단) 불릿 목록 끝에 constraints 카드 한 줄 추가**

```markdown
- FONT·STYLE·MODE(라이트/다크)는 형용사가 아니라 **명시값**으로 못박는다(constraints 카드): "Font: geometric sans, heavy weight. Style: matte 3D clay render. Mode: dark." 값이 고정돼야 컷 간 일관성이 유지된다.
```

- [ ] **Step 2: §2.6 뒤에 신규 소절 §2.7 추가**

```markdown
### 2.7 변형 > 재롤 (반복 규율)

- 시스템(레이아웃·정보 위계·확정 카피)을 1회 고정한 뒤, 개선은 **한 번에 변수 하나만** 바꾼다 — 각도, 크롭, 액센트 색, 배경 톤 중 하나씩. 여러 변수를 동시에 바꾸면 무엇이 좋아졌는지 알 수 없다.
- 부분 개선은 후속 수정 프롬프트(§2.6)로, 전체 재생성(reroll)은 §1의 즉시 탈락 기준을 어겼을 때만 한다.
```

- [ ] **Step 3: §2.5(참조 이미지) 끝에 REFERENCE-DRIVEN 링크 추가**

```markdown
- 레퍼런스를 아트디렉션 입력으로 본격 활용하는 생성(스타일 트랜스퍼·1레퍼런스→N브랜드)은 [REFERENCE-DRIVEN.md](REFERENCE-DRIVEN.md)의 근접도 다이얼·visual DNA·저작권 가드레일을 함께 따른다.
```

- [ ] **Step 4: §4(온스크린 텍스트 정책) 표 뒤 불릿 목록에 2-pass 한 줄 추가**

`| 텍스트가 이미지의 주체…` 불릿들 근처에 추가:

```markdown
- **2-pass 타이포**: 텍스트가 주체가 아닌 컷은 1차로 텍스트 없이(오버레이 안전영역을 비워) 생성하고, 로고·긴 카피는 코드 렌더·편집 도구로 2차 합성한다 — 생성 모델의 취약한 타이포에 정본 텍스트를 맡기지 않는다.
```

- [ ] **Step 5: 검증 — 링크 해석 + 소절 존재**

Run: `grep -nE '2\.7 변형 > 재롤|constraints 카드|2-pass 타이포|REFERENCE-DRIVEN\.md' skills/gx-design/PROMPT-PLAYBOOK.md && test -f skills/gx-design/REFERENCE-DRIVEN.md && echo LINK_OK`
Expected: 네 패턴 매치 + `LINK_OK`(링크 대상 파일 실재).

- [ ] **Step 6: 커밋**

```bash
git add skills/gx-design/PROMPT-PLAYBOOK.md
git commit -m "feat: PROMPT-PLAYBOOK 보강 — 변형>재롤 규율·constraints 카드·2-pass·REFERENCE-DRIVEN 링크

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: 수용 체크(Acceptance Checks) — creative-production·creative-review 페어링

**Files:**
- Modify: `skills/creative-production/SKILL.md` (매체별 필수 섹션, 제작 원칙/UX-UI)
- Modify: `skills/creative-review/SKILL.md` (제작 가능성 절)

**Interfaces:**
- Consumes: Task 1 `REFERENCE-DRIVEN.md §4`(수용 체크의 저작권 가드 항이 이를 참조).
- Produces: 표준 섹션명 **"수용 체크 (Acceptance Checks)"** — creative-review가 동일 명칭으로 대조. 두 파일에서 명칭 철자 일치 필수.

- [ ] **Step 1: creative-production 공통 필수 섹션에 "수용 체크" 추가**

`## 매체별 필수 섹션` 아래 `- 공통:` 줄을 수정 — 끝에 ` / 수용 체크`를 덧붙인다:

```markdown
- 공통: 제작 목표 / 적용 전략 / 제작 명세 / 자체 검수 결과 / 미확정 사항 / 수용 체크
```

- [ ] **Step 2: creative-production에 수용 체크 정의 섹션 추가**

`## 매체별 필수 섹션`의 매체 불릿(BX/그래픽/UX-UI/영상) 뒤, "위임 프롬프트에 분량 상한이…" 문장 앞에 추가:

```markdown
### 수용 체크 (Acceptance Checks)

명세 말미에 "이 산출물이 맞다고 볼 조건"을 체크리스트로 명시한다 — vibe가 아니라 확인 가능한 조건으로. 최소 포함: 반응형 범위(해당 시), 접근성(키보드 포커스·텍스트 대비·reduced-motion, 해당 시), 성능(모션은 transform·opacity), 시각 위계(시선 순서), 그리고 레퍼런스를 썼다면 저작권 가드([REFERENCE-DRIVEN.md](../gx-design/REFERENCE-DRIVEN.md) §4) 위반 0건. 검수(creative-review)는 이 체크를 판정 기준으로 쓴다.

UX/UI 산출물에서 생성형 UI 프롬프트가 필요하면 GOAL·FORMAT·LAYOUT(말로 쓴 와이어프레임)·TYPE·COLOR+MATERIAL·IMAGERY·COPY(정확히 렌더)·CONSTRAINTS·NEGATIVE 9블록으로 스켈레톤화하고, 변형은 한 번에 1변수만 바꾼다(PROMPT-PLAYBOOK §2.7).
```

- [ ] **Step 3: creative-review 제작 가능성 절에 수용 체크 항 추가**

`### 제작 가능성` 불릿 목록 끝에 추가:

```markdown
- 명세의 수용 체크(Acceptance Checks) 조건을 실제로 충족하는가? (creative-production 수용 체크 항목 대조 — 미충족은 Critical/Major로 분류)
```

- [ ] **Step 4: 검증 — 명칭 철자 일치**

Run: `grep -rn '수용 체크' skills/creative-production/SKILL.md skills/creative-review/SKILL.md`
Expected: 양쪽 파일에 "수용 체크" 존재, 표기 동일. creative-production에 정의 섹션 + 9블록 스켈레톤, creative-review에 대조 항.

- [ ] **Step 5: 커밋**

```bash
git add skills/creative-production/SKILL.md skills/creative-review/SKILL.md
git commit -m "feat: 수용 체크(Acceptance Checks) 표준 섹션 — 제작 명시·검수 대조 페어링

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: 배달·메타 (SKILL 배달 + README + 버전)

**Files:**
- Modify: `skills/gx-design/SKILL.md` (단계 3 Production)
- Modify: `README.md` (구성 문단 + FAQ + 필요 시 버전)
- Modify: `.claude-plugin/plugin.json` (version)
- Modify: `.claude-plugin/marketplace.json` (설명 — 해당 필드 존재 시)

**Interfaces:**
- Consumes: Task 1 `REFERENCE-DRIVEN.md` 경로.
- Produces: 사용자향 문서·버전 정합.

- [ ] **Step 1: gx-design/SKILL.md 단계 3에 REFERENCE-DRIVEN 배달 문장 추가**

`## 단계 3 — Production`에서 VISUAL-CRAFT.md 경로를 위임 프롬프트에 포함하는 문장 근처에 추가:

```markdown
레퍼런스 이미지·영상을 아트디렉션 입력으로 쓰는 제작(스타일 트랜스퍼·1레퍼런스→N브랜드)이면 위임 프롬프트에 REFERENCE-DRIVEN.md 경로도 포함한다(근접도 다이얼·visual DNA·저작권 가드레일 — 타인 자산 재현 금지).
```

- [ ] **Step 2: README.md 구성 문단에 REFERENCE-DRIVEN 등재**

`gx-design/` 참조 파일을 나열하는 줄(… VISUAL-CRAFT.md(안티-슬롭…)) 끝에 추가:

```markdown
 · REFERENCE-DRIVEN.md(레퍼런스 구동 생성 — 근접도 다이얼·저작권 가드레일)
```

- [ ] **Step 3: README.md FAQ "AI가 만든 티" 항목에 저작권 가드 한 줄 추가**

해당 FAQ 답변 끝에 추가:

```markdown
 레퍼런스 이미지를 참고해 생성할 때는 REFERENCE-DRIVEN 규칙이 워드마크·letterform·유명 시그니처의 그대로 재현을 막습니다(참고는 하되 베끼지 않음).
```

- [ ] **Step 4: plugin.json 버전 상향**

먼저 현재 값 확인: `grep '"version"' .claude-plugin/plugin.json`
그다음 `"version": "0.6.0"` → `"version": "0.7.0"`으로 수정(현재 값이 0.6.0이 아니면 현재값 → 그 다음 minor로 올림).

- [ ] **Step 5: marketplace.json 확인·정합**

Run: `grep -nE 'version|description' .claude-plugin/marketplace.json`
description에 버전/기능 문구가 있으면 REFERENCE-DRIVEN(레퍼런스 구동 생성) 반영, version 필드가 있으면 0.7.0으로 맞춘다. 없으면 변경 없이 통과.

- [ ] **Step 6: 검증 — 버전 정합 + 링크**

Run: `grep -rn '0.7.0' .claude-plugin/plugin.json && grep -n 'REFERENCE-DRIVEN' README.md skills/gx-design/SKILL.md`
Expected: plugin.json 0.7.0, README·SKILL.md에 REFERENCE-DRIVEN 참조 존재.

- [ ] **Step 7: 커밋**

```bash
git add skills/gx-design/SKILL.md README.md .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "feat: REFERENCE-DRIVEN 배달·문서·버전 0.7.0

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: 리뷰 패스 (규격 정합·라이선스·문체)

**Files:**
- Review only (수정은 발견 시): 위 전 파일.

**Interfaces:**
- Consumes: Task 1~5 산출 전부.

- [ ] **Step 1: 리뷰 서브에이전트 1개 스폰**

프롬프트 요지: "브랜치 `feat/absorb-mengto-rules`의 변경(REFERENCE-DRIVEN.md 신규 + VISUAL-CRAFT·PROMPT-PLAYBOOK·creative-production·creative-review·SKILL·README·plugin.json 보강)을 스펙 `docs/superpowers/specs/2026-07-24-absorb-mengto-design-rules-design.md` 대비 검수하라. 확인: (1) MIT 원문 문장 복붙이 없고 규칙 재서술인가, (2) 교차 참조 링크(REFERENCE-DRIVEN↔PROMPT-PLAYBOOK, 수용 체크 명칭 일치)가 깨지지 않았나, (3) 버전 0.7.0 정합, (4) 톤 기준 상위 원칙이 REFERENCE-DRIVEN에 명시됐나, (5) 기존 문단 훼손·문체 이탈. Critical/Major/Minor로 보고."

- [ ] **Step 2: Critical/Major 수정**

리뷰가 Critical/Major를 내면 해당 파일을 수정하고 그 파일만 재커밋. Minor는 기록만.

- [ ] **Step 3: 최종 확인 커밋(수정 있었을 때만)**

```bash
git add -A && git commit -m "fix: 리뷰 반영 — <요지>

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 4: 완료 보고**

변경 요약(파일 6+1, 버전 0.7.0) + 다음 단계(로컬 재설치 검증 또는 PR)를 사용자에게 보고. 릴리즈(태그·PR)는 사용자 요청 시에만.

---

## Self-Review (작성자 체크 결과)

**1. 스펙 커버리지:**
- REFERENCE-DRIVEN(근접도·visual DNA·저작권 가드·brand matrix·검수연계) → Task 1 ✓
- VISUAL-CRAFT §1·§2(부정정의·워치리스트·룩별 다이얼) → Task 2 ✓
- PROMPT-PLAYBOOK(variants>rerolls·constraints 카드·2-pass·링크) → Task 3 ✓
- 수용 체크(creative-production/review) + 9블록 UI 스켈레톤 선택 참조 → Task 4 ✓
- 배달(SKILL 단계3)·README·plugin.json 0.7.0·marketplace → Task 5 ✓
- 실행방식(리뷰 서브에이전트 1개) → Task 6 ✓
- 비목표(코드 레시피·에셋·#6·#7 제외)는 태스크에 없음 = 의도된 제외 ✓

**2. 플레이스홀더 스캔:** 각 편집 스텝에 최종 텍스트 블록 포함, TBD/TODO 없음. plugin.json/marketplace는 "현재값 확인 후 수정"으로 구체화(하드코딩 라인 추정 회피).

**3. 타입/명칭 정합:** 파일 경로 `skills/gx-design/REFERENCE-DRIVEN.md` 전 태스크 일치. 섹션 명칭 "수용 체크 (Acceptance Checks)" Task 4 양쪽 동일. §번호 참조(§2.6·§2.7·§4) 실제 파일 구조와 일치. 상대경로 링크: PROMPT-PLAYBOOK→REFERENCE-DRIVEN 동일 디렉터리(`REFERENCE-DRIVEN.md`), creative-production→REFERENCE-DRIVEN 교차 디렉터리(`../gx-design/REFERENCE-DRIVEN.md`) 정확.
```
