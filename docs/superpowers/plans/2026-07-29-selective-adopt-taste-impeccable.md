# taste·impeccable 선택 도입 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** taste-skill(MIT)·impeccable(Apache 2.0)에서 결과물 품질을 올리는 규칙만 선택 재서술 — 신규 ANTI-TELL-CHECKLIST.md(요소·카피·구조 텔) + 기존 파일 보강 + impeccable detect CLI의 가용 시 선택 게이트.

**Architecture:** 신규 참조 파일 1개(`skills/gx-design/ANTI-TELL-CHECKLIST.md`)에 요소 레벨 텔 점검표를 중앙화하고, VISUAL-CRAFT(§1 4번째 룩·§3 폰트 밴·§6 링크)·VISUAL-QUALITY(기계 바닥 점검 + detect 선택 게이트)·creative-production/review(자체 점검·검수 항)를 외과적으로 보강한다. detect는 npx 1회 실행(설치·훅 없음), 미가용 시 체크리스트 수동 점검 폴백.

**Tech Stack:** 마크다운 스킬 파일 + Claude Code 플러그인 매니페스트(`.claude-plugin/`). 빌드·테스트 프레임워크 없음 — 검증은 grep + 링크 실재 확인 + 리뷰 서브에이전트.

## Global Constraints

모든 태스크에 암묵 적용:
- **선행 조건**: v0.7(MengTo 흡수)이 머지되어 `plugin.json` version이 `0.7.0`이어야 한다. 아니면 **작업을 중단하고 사용자에게 보고**한다(이 계획의 앵커 일부가 v0.7 산출 텍스트에 의존).
- 버전 `0.7.0` → `0.8.0` (minor).
- 도입은 **규칙 재서술** — taste(MIT)·impeccable(Apache 2.0) 원문 문장 복붙 금지. 규칙 아이디어만 한국어·우리 매체(Gemini 웹 생성·코드 렌더) 맥락으로 새로 쓴다.
- 모든 항목은 하드 밴이 아니라 "무심코 기본값" 금지 — **브리프·톤 기준이 요구하면 그쪽이 이긴다** 프레임을 유지한다.
- `ANTI-TELL-CHECKLIST.md`는 얇게 유지(빈 줄 포함 45~85줄).
- detect는 선택 게이트 — 새 하드 의존·설치 요구·훅 등록을 만들지 않는다.
- 기존 파일 문체 유지(한국어, 간결, 번호 섹션). 커밋은 브랜치 `feat/selective-adopt-taste-impeccable`(main에서 분기).
- 커밋 트레일러: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- 원자료가 필요하면(재서술 대조용): taste 원문 = github.com/Leonxlnx/taste-skill `skills/taste-skill/SKILL.md`, impeccable 규칙 = github.com/pbakaus/impeccable `.claude/skills/impeccable/scripts/detector/registry/antipatterns.mjs`. 이 계획의 태스크에는 최종 텍스트가 전부 들어 있으므로 평소엔 불필요.

---

### Task 1: 신규 ANTI-TELL-CHECKLIST.md 작성

**Files:**
- Create: `skills/gx-design/ANTI-TELL-CHECKLIST.md`

**Interfaces:**
- Consumes: 없음(독립). 단 Step 1에서 선행 조건·브랜치를 확정한다.
- Produces: 파일 경로 `skills/gx-design/ANTI-TELL-CHECKLIST.md`와 섹션 앵커 `§1 요소 레벨 시각 텔`·`§2 카피·콘텐츠 텔`·`§3 구조 수치 가드`·`§4 사용법`. Task 2(VISUAL-CRAFT 링크)·Task 3(VISUAL-QUALITY 링크)·Task 4(production/review 참조)·Task 5(SKILL 배달·README)가 이 경로·§번호에 의존.

- [ ] **Step 1: 선행 조건 확인 + 브랜치 생성**

Run: `grep '"version"' .claude-plugin/plugin.json`
Expected: `"version": "0.7.0"` — 아니면 여기서 중단하고 사용자에게 "v0.7 미머지" 보고.

```bash
git checkout main && git pull && git checkout -b feat/selective-adopt-taste-impeccable
```

- [ ] **Step 2: 파일 생성**

아래 내용으로 `skills/gx-design/ANTI-TELL-CHECKLIST.md`를 만든다:

```markdown
# ANTI-TELL-CHECKLIST — 요소·카피·구조 AI-티 점검표

[VISUAL-CRAFT.md](VISUAL-CRAFT.md) §1이 룩(look) 단위의 AI 기본값을 잡는다면, 이 문서는 **요소·카피·구조 단위**의 티(tell)를 잡는다. 제작(creative-production)의 완료 전 자체 점검과 검수(creative-review)의 시각 완성도 검수가 공통으로 쓴다.
근거: impeccable(Apache 2.0) 탐지 규칙과 taste-skill(MIT)의 프로덕션 관찰 규칙에서 우리 매체(Gemini 웹 생성·코드 렌더)에 맞는 것만 선택해 우리 규격으로 재서술한 것이다 — 원문 복제 아님, 외부 런타임 의존 없음.

**적용 원칙**
- 모든 항목은 "무심코 기본값" 금지다. **브리프·톤 기준이 요구하면 그쪽이 이긴다** — 이탈이 의도면 근거를 명세·로그에 기록하고 통과시킨다.
- 적용 범위: UI·그래픽·코드 렌더·Gemini 웹 생성 산출물. §1의 모션성 항목(마퀴·펄싱)과 §3은 화면 산출물에만 해당한다.
- 코드 렌더는 [VISUAL-QUALITY.md](VISUAL-QUALITY.md)의 detect 선택 게이트가 이 목록의 상당수를 기계 검사한다 — 게이트를 돌렸으면 겹치는 항목은 그 출력으로 갈음한다.

## 1. 요소 레벨 시각 텔

- [ ] 카드 한쪽에 두꺼운 색 테두리(side-tab 액센트)를 두지 않았다 — 가장 대표적인 AI-UI 표식.
- [ ] 텍스트에 그라데이션을 입히지 않았다.
- [ ] 색 글로우 그림자, 어두운 배경 위 방사형 halo·스포트라이트 빛 번짐을 장식으로 쓰지 않았다.
- [ ] 카드 안에 카드를 넣지 않았다 — 여백과 선으로 나눈 납작한 구조를 썼다.
- [ ] 모든 간격이 같은 값으로 단조롭지 않다 — 위계에 따라 리듬이 있다.
- [ ] 제목 위 아이콘 타일, 히어로의 eyebrow 칩·kicker 라벨을 습관적으로 얹지 않았다.
- [ ] 가짜 생동감이 없다 — 펄싱 상태 점, 장식용 깜빡이 커서, 자동 스크롤 마퀴(부득이하면 페이지당 1개).
- [ ] 이탤릭 세리프 디스플레이 제목, 화면을 채우는 과대 h1, 가독성을 해치는 과압축 자간이 없다.
- [ ] 원시 도형을 조립한 자리표시자식 일러스트가 없다.
- [ ] 동일한 카드 3개를 나란히 세운 그리드가 없다. 좌우 교대 이미지+텍스트 스플릿은 연속 2개까지만 썼다.

## 2. 카피·콘텐츠 텔

- [ ] 제네릭 인명·아바타(John Doe·홍길동류)와 완벽한 숫자(99.99%·10x)가 없다 — 주제 맥락에서 나올 법한 이름·수치를 썼다.
- [ ] 슬롭 브랜드명(Acme·Nexus·Cloudly류)이 없다.
- [ ] 필러 동사·buzzword가 없다 — 영문 Elevate·Seamless·Unleash·streamline류, 한국어 "혁신적인"·"획기적인"·"손쉽게" 남용.
- [ ] 짧은 대조·경구 반복 어투(aphoristic cadence)로 카피를 채우지 않았다.
- [ ] 영문 카피에 em-dash(—)를 남발하지 않았다(한국어 문장부호 관습에는 이 항목을 적용하지 않는다).
- [ ] 가짜 캡션("Field study no.12"류), 히어로의 버전 라벨(BETA·V0.6), 스크롤 큐("↓ scroll"), 로케일/날씨 스트립이 없다.
- [ ] div로 조립한 가짜 스크린샷·대시보드가 없다 — 실제 렌더, 생성 이미지, 실제 컴포넌트 프리뷰만 썼다.

## 3. 구조 수치 가드 (웹/UI 화면)

- [ ] 히어로의 텍스트 요소는 최대 4개다(eyebrow·headline·subtext·CTA) — 신뢰 스트립·가격 티저는 히어로 밖으로.
- [ ] 히어로 서브텍스트는 짧다(영문 ~20단어, 한국어는 두 문장 이내 등가) — 첫 CTA가 스크롤 없이 보인다.
- [ ] eyebrow 라벨은 3섹션당 최대 1개만 썼다.
- [ ] 데스크톱 네비게이션이 한 줄이다.

## 4. 사용법

- **제작**: 완료 전 위 항목을 1회 점검한다. 걸린 항목은 수정하거나, 브리프가 요구한 선택이면 근거를 "자체 검수 결과"에 기록한다.
- **검수**: 시각 완성도 검수의 입력이다 — 근거 기록 없는 위반은 Major 이상으로 분류한다.
- **detect 게이트와의 관계**: §1의 대부분과 §2 일부(em-dash·buzzword)는 detect가 기계 검사한다. §2 한국어 항목과 §3 수치 가드는 기계가 못 잡으므로 항상 수동 점검한다.
```

- [ ] **Step 3: 검증 — 섹션·분량·재서술**

Run: `grep -nE '^## [0-9]' skills/gx-design/ANTI-TELL-CHECKLIST.md && wc -l < skills/gx-design/ANTI-TELL-CHECKLIST.md`
Expected: §1~§4 네 섹션 출력, 줄 수 45~85. "side-tab"·"홍길동"·"em-dash" 항목 존재(`grep -c '\- \[ \]'` ≥ 20). 영어 원문 문장 복붙 없음.

- [ ] **Step 4: 커밋**

```bash
git add skills/gx-design/ANTI-TELL-CHECKLIST.md
git commit -m "feat: 요소·카피·구조 AI-티 점검표 신설(ANTI-TELL-CHECKLIST) — taste·impeccable 선택 재서술

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: VISUAL-CRAFT.md 보강 (4번째 룩·팔레트 신호·폰트 밴·링크)

**Files:**
- Modify: `skills/gx-design/VISUAL-CRAFT.md` (근거 줄, §1, §3, §6)

**Interfaces:**
- Consumes: Task 1의 `ANTI-TELL-CHECKLIST.md` 경로(링크 대상). Task 1 완료 후 실행.
- Produces: §1이 "4대 기본 룩"이 됨 — Task 3(VISUAL-QUALITY)·Task 4(creative-review)·Task 5(README)의 "3종/3대 → 4종/4대" 표기 갱신이 이에 의존.

- [ ] **Step 1: 근거 줄(파일 상단) 출처 갱신**

`근거: Anthropic frontend-design 공식 스킬 원칙 + 커뮤니티 taste·animate 스킬의 구체 규칙을 우리 규격으로 **흡수**한 것이다(외부 스킬 런타임 의존 없음).` 를 다음으로 교체:

```markdown
근거: Anthropic frontend-design 공식 스킬 원칙 + 커뮤니티 taste·animate 스킬의 구체 규칙 + impeccable 탐지 규칙 일부를 우리 규격으로 **흡수**한 것이다(외부 스킬 런타임 의존 없음).
```

- [ ] **Step 2: §1 — 3대 → 4대, 4번째 룩 추가, 룩 1 신호 보강**

`AI 생성 디자인이 몰리는 3대 기본 룩` → `AI 생성 디자인이 몰리는 4대 기본 룩`으로 교체.

`1. 크림 배경(#F4F1EA류) + 고대비 세리프 디스플레이 + 테라코타 악센트` 끝에 ` — 프리미엄 소비재 변형(크림·브라스·옥스블러드·에스프레소 조합) 포함` 을 덧붙인다.

`3. 브로드시트 레이아웃 + 헤어라인 룰 + radius 0 + 신문형 밀집 컬럼` 다음 줄에 추가:

```markdown
4. AI 퍼플/시안 콤보 — 보라→파랑·시안으로 흐르는 그라데이션 악센트(생성 UI의 가장 유명한 신호)
```

v0.7이 추가한 워치리스트 문단의 `위 3대 룩 외에도` → `위 4대 룩 외에도`로 교체.

- [ ] **Step 3: §1 — 팔레트 재사용 금지 불릿 추가**

`- 자유로운 축은 위 기본값이 아니라 "이 브리프·주제만의 선택"으로 채운다.` 불릿 바로 뒤(워치리스트 문단 앞)에 추가:

```markdown
- 같은 레포의 직전 산출물과 근거 없이 동일한 팔레트를 재사용하지 않는다 — outputs/의 기존 산출물과 겹치면 의도인지 확인한다.
```

- [ ] **Step 4: §1 끝에 요소 레벨 텔 링크 문단 추가**

§1의 마지막 문단(v0.7의 "부정 정의로 룩 못박기" 문단) 뒤에 추가:

```markdown

**요소 레벨 텔은 별도 점검표로** — 룩을 피해도 요소 단위(side-tab 보더·그래디언트 텍스트·글로우 배경·가짜 생동감)와 카피에서 티가 난다. 제작·검수는 [ANTI-TELL-CHECKLIST.md](ANTI-TELL-CHECKLIST.md)를 함께 쓴다.
```

- [ ] **Step 5: §3 — 타이포 불릿 교체(폰트 밴 구체화)**

`- 타이포: display·body(필요 시 utility) 역할을 의도적으로 페어링한다. 흔한 기본 폰트(Inter·Roboto·Arial 등 AI가 남용하는 폰트)에 무심코 기대지 않는다.` 를 다음으로 교체:

```markdown
- 타이포: display·body(필요 시 utility) 역할을 의도적으로 페어링한다. 흔한 기본 폰트(Inter·Roboto·Arial 등 AI가 남용하는 폰트)와 LLM 애용 디스플레이 세리프(Fraunces·Instrument Serif)에 무심코 기대지 않는다. "크리에이티브하니까 세리프"라는 기본값 판단도 텔이다 — 세리프는 브리프·장르가 요구할 때만 쓴다.
```

- [ ] **Step 6: §6 끝에 콘텐츠 텔 링크 추가**

§6(카피도 디자인 재료) 불릿 목록 끝에 추가:

```markdown
- 콘텐츠도 텔이 된다 — 제네릭 인명·완벽한 숫자·필러 동사·가짜 캡션은 [ANTI-TELL-CHECKLIST.md](ANTI-TELL-CHECKLIST.md) §2로 점검한다.
```

- [ ] **Step 7: 검증**

Run: `grep -nE '4대 기본 룩|AI 퍼플/시안 콤보|옥스블러드|Fraunces|ANTI-TELL-CHECKLIST' skills/gx-design/VISUAL-CRAFT.md && grep -c '3대' skills/gx-design/VISUAL-CRAFT.md`
Expected: 다섯 패턴 모두 매치. '3대' 카운트 0(모두 4대로 갱신). 기존 §2·§4·§5 문단 훼손 없음.

- [ ] **Step 8: 커밋**

```bash
git add skills/gx-design/VISUAL-CRAFT.md
git commit -m "feat: VISUAL-CRAFT 보강 — 4번째 기본 룩(AI 퍼플/시안)·팔레트 신호·폰트 밴·ANTI-TELL 링크

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: VISUAL-QUALITY.md 보강 (기계 바닥 점검 + detect 선택 게이트)

**Files:**
- Modify: `skills/gx-design/VISUAL-QUALITY.md` (절차 3, 신규 섹션, 검수 연계)

**Interfaces:**
- Consumes: Task 1 `ANTI-TELL-CHECKLIST.md` 경로, Task 2의 "4대" 표기.
- Produces: 섹션 제목 `## detect 선택 게이트 (선택 — 코드 렌더 산출물만)` — Task 4(creative-review의 detect 해석 항)가 이 게이트의 존재를 전제.

- [ ] **Step 1: 절차 3 크래프트 불릿 교체(4대 표기 + ANTI-TELL 추가)**

`   - **크래프트([VISUAL-CRAFT.md](VISUAL-CRAFT.md))**: 안티-슬롭(§1 3대 기본 룩을 무심코 답습하지 않았는가) / 일관성 잠금(§3 accent·radius·테마가 각 하나인가) / 모션(§4 있으면 transform·opacity·나가는 모션<들어오는 모션인가) / 시그니처(§5 대담함이 한 곳에 모였는가)` 를 다음으로 교체:

```markdown
   - **크래프트([VISUAL-CRAFT.md](VISUAL-CRAFT.md))**: 안티-슬롭(§1 4대 기본 룩을 무심코 답습하지 않았는가) / 일관성 잠금(§3 accent·radius·테마가 각 하나인가) / 모션(§4 있으면 transform·opacity·나가는 모션<들어오는 모션인가) / 시그니처(§5 대담함이 한 곳에 모였는가) / 요소·카피 텔([ANTI-TELL-CHECKLIST.md](ANTI-TELL-CHECKLIST.md) — side-tab 보더·그래디언트 텍스트·가짜 생동감·콘텐츠 텔)
```

- [ ] **Step 2: 절차 3에 기계 바닥 불릿 추가**

위에서 교체한 크래프트 불릿 바로 다음 줄에 추가:

```markdown
   - **기계 바닥**: 대비 WCAG AA(본문 4.5:1·큰 텍스트 3:1) / 본문 크기 최소 14px(권장 16) / 본문 line-height 1.4 이상 / 줄 길이 과장(영문 ~80자·한글 ~40자 초과 경계) / 헤딩 레벨 건너뜀 / 색 배경 위 회색 본문 / 오버플로·요소 가림. 코드 렌더면 아래 detect 선택 게이트 출력을 이 항목들의 기계 근거로 쓴다.
```

- [ ] **Step 3: 절차 섹션과 "## 검수 연계" 사이에 신규 섹션 추가**

```markdown
## detect 선택 게이트 (선택 — 코드 렌더 산출물만)

impeccable(Apache 2.0)의 탐지 CLI를 **가용할 때만** 기계 검사로 빌려 쓴다. Playwright MCP와 같은 "가용 시 사용·미가용 시 폴백" 패턴이며, 스킬·훅 설치가 아니다(impeccable의 .claude 설치·훅은 도입하지 않는다).

- **실행 조건**: 산출물이 HTML/CSS 코드 렌더이고 node·npx가 가용할 때. 미가용이면 [ANTI-TELL-CHECKLIST.md](ANTI-TELL-CHECKLIST.md) 수동 점검으로 갈음한다.
- **실행**: `npx --yes impeccable@latest detect <렌더 폴더>` 1회. 무출력이면 통과다.
- **해석**: error(스크립트 오류·콘텐츠 비가시 등) = Critical 상당 → 즉시 수정 / 기본 항목 = 절차 3의 비평 대상 / advisory = 참고.
- **기계 출력은 입력이지 판정자가 아니다**: 브리프·디자인 톤 기준이 의도한 선택(예: 요청된 크림 팔레트)을 지적하면 브리프 우선으로 기각하고, 기각 사유를 렌더 품질 로그에 남긴다.
- **톤 기준 시너지**: DESIGN.md 톤 기준이 프로젝트에 있으면 detect의 design-system 계열 규칙이 폰트·색·radius·타입 스케일 이탈을 기계 검사한다 — 검수 축 A의 보조 입력.
```

- [ ] **Step 4: "## 검수 연계"에 detect 첨부 불릿 추가**

검수 연계 섹션 불릿 목록 끝에 추가:

```markdown
- detect 게이트를 실행했으면 출력 전문(또는 "무출력 = 통과")을 렌더 품질 로그에 첨부한다.
```

- [ ] **Step 5: 검증**

Run: `grep -nE 'detect 선택 게이트|기계 바닥|ANTI-TELL-CHECKLIST|impeccable@latest' skills/gx-design/VISUAL-QUALITY.md && grep -c '3대' skills/gx-design/VISUAL-QUALITY.md`
Expected: 네 패턴 매치, '3대' 카운트 0. Red Flags 섹션 등 기존 문단 훼손 없음.

- [ ] **Step 6: 커밋**

```bash
git add skills/gx-design/VISUAL-QUALITY.md
git commit -m "feat: VISUAL-QUALITY 보강 — 기계 바닥 점검·impeccable detect 선택 게이트(가용 시)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: creative-production 자체 점검 + creative-review 검수 항

**Files:**
- Modify: `skills/creative-production/SKILL.md` (제작 원칙 불릿 목록)
- Modify: `skills/creative-review/SKILL.md` (시각 완성도 절)

**Interfaces:**
- Consumes: Task 1 경로(교차 디렉터리 상대경로 `../gx-design/ANTI-TELL-CHECKLIST.md`), Task 3의 detect 게이트 존재.
- Produces: 검수 어휘 "근거 기록 없는 위반은 Major 이상" — ANTI-TELL-CHECKLIST §4와 표현 일치 필수.

- [ ] **Step 1: creative-production 제작 원칙에 자체 점검 불릿 추가**

`- UI·그래픽·코드 렌더 산출물은 gx-design 스킬의 VISUAL-CRAFT 규격을 따른다 — …` 불릿 바로 뒤에 추가:

```markdown
- UI·그래픽·코드 렌더·Gemini 웹 생성 산출물은 완료 전 gx-design 스킬의 ANTI-TELL-CHECKLIST(요소·카피·구조 텔 점검표)를 1회 자체 점검한다 — 걸린 항목은 수정하거나, 브리프가 요구한 선택이면 근거를 "자체 검수 결과"에 기록한다.
```

- [ ] **Step 2: creative-review 시각 완성도 절 보강**

`- (UI·그래픽·코드 렌더) 안티-슬롭 — AI 기본 룩 3종을 무심코 답습하지 않았는가? (VISUAL-CRAFT §1)` 를 다음으로 교체:

```markdown
- (UI·그래픽·코드 렌더) 안티-슬롭 — AI 기본 룩 4종을 무심코 답습하지 않았는가? (VISUAL-CRAFT §1)
```

이어서 같은 불릿 목록의 모션 불릿(`- (모션 있는 산출물) …`) 뒤에 두 항 추가:

```markdown
- (UI·그래픽·코드 렌더) 요소·카피 텔 — ANTI-TELL-CHECKLIST 항목을 위반하지 않았는가? 근거 기록 없는 위반은 Major 이상.
- (코드 렌더) detect 출력이 첨부됐으면 — error = Critical 상당, 기본 항목 = 비평 대상, advisory = 참고로 해석한다. 브리프가 의도한 선택을 기계가 지적한 경우 기각 사유가 기록됐는지 확인한다.
```

- [ ] **Step 3: 검증 — 어휘 일치**

Run: `grep -n 'ANTI-TELL-CHECKLIST' skills/creative-production/SKILL.md skills/creative-review/SKILL.md && grep -c '3종' skills/creative-review/SKILL.md`
Expected: 양쪽 파일에 ANTI-TELL-CHECKLIST 존재, '3종' 카운트 0. "Major 이상" 표현이 checklist §4와 동일.

- [ ] **Step 4: 커밋**

```bash
git add skills/creative-production/SKILL.md skills/creative-review/SKILL.md
git commit -m "feat: 제작 자체 점검·검수 항 — ANTI-TELL-CHECKLIST 페어링 + detect 출력 해석 규칙

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: 배달·메타 (SKILL 배달 + README + 버전 0.8.0)

**Files:**
- Modify: `skills/gx-design/SKILL.md` (단계 3 Production)
- Modify: `skills/gx-redesign/SKILL.md` (VISUAL-CRAFT 배달 줄)
- Modify: `README.md` (구성 줄 + FAQ)
- Modify: `.claude-plugin/plugin.json` (version)
- Modify: `.claude-plugin/marketplace.json` (설명 — 해당 필드 존재 시)

**Interfaces:**
- Consumes: Task 1 경로, Task 2의 "4종" 표기.
- Produces: 사용자향 문서·버전 정합.

- [ ] **Step 1: gx-design/SKILL.md 단계 3 배달 문장 확장**

단계 3의 `UI·그래픽·UX/UI 산출물은 VISUAL-CRAFT.md 경로도 위임 프롬프트에 포함한다(안티-슬롭·톤 다이얼·일관성·모션 — 렌더 없이 명세만 만드는 잡도 서브에이전트가 규칙 원문에 닿도록).` 문장 바로 뒤에 추가:

```markdown
같은 산출물에는 ANTI-TELL-CHECKLIST.md 경로도 함께 배달한다(요소·카피·구조 텔 자체 점검 — 완료 전 1회).
```

- [ ] **Step 2: gx-redesign/SKILL.md 배달 줄 확장**

`UI·그래픽·UX/UI 산출물은 [../gx-design/VISUAL-CRAFT.md](../gx-design/VISUAL-CRAFT.md) 경로도 위임 프롬프트에 포함한다(안티-슬롭·톤 다이얼·일관성·모션).` 를 다음으로 교체:

```markdown
UI·그래픽·UX/UI 산출물은 [../gx-design/VISUAL-CRAFT.md](../gx-design/VISUAL-CRAFT.md)와 [../gx-design/ANTI-TELL-CHECKLIST.md](../gx-design/ANTI-TELL-CHECKLIST.md) 경로도 위임 프롬프트에 포함한다(안티-슬롭·톤 다이얼·일관성·모션 + 요소·카피 텔 점검).
```

- [ ] **Step 3: README 구성 줄에 등재**

`gx-design/` 구성 줄 끝(v0.7이 추가한 ` · REFERENCE-DRIVEN.md(…)` 뒤)에 추가:

```markdown
 · ANTI-TELL-CHECKLIST.md(요소·카피·구조 AI-티 점검표)
```

- [ ] **Step 4: README FAQ "AI가 만든 티" 항목 갱신**

해당 답변에서 두 가지 치환 + 한 문장 추가(v0.7이 덧붙인 문장은 보존):
- `AI가 몰리는 기본 룩 3종을 회피하고` → `AI가 몰리는 기본 룩 4종을 회피하고`
- `Anthropic 공식 frontend-design 원칙 + taste·animate 커뮤니티 스킬의 구체 규칙을 흡수한 것으로` → `Anthropic 공식 frontend-design 원칙 + taste·animate·impeccable 커뮤니티 스킬의 구체 규칙을 선택 재서술로 흡수한 것으로`
- 답변 끝에 추가:

```markdown
 요소 단위 티(side-tab 보더·그래디언트 텍스트·가짜 생동감)와 카피 티(제네릭 인명·필러 동사)는 ANTI-TELL-CHECKLIST가 제작·검수에서 점검하고, 코드 렌더 산출물은 impeccable detect CLI가 가용하면 기계 검사로 보강합니다(설치 불필요 — npx 1회 실행, 미가용 시 수동 점검).
```

- [ ] **Step 5: plugin.json 버전 상향**

먼저 확인: `grep '"version"' .claude-plugin/plugin.json`
`"version": "0.7.0"` → `"version": "0.8.0"` (현재 값이 0.7.0이 아니면 중단하고 보고 — Global Constraints 선행 조건 위반).

- [ ] **Step 6: marketplace.json 확인·정합**

Run: `grep -nE 'version|description' .claude-plugin/marketplace.json`
description에 기능 문구가 있으면 "요소·카피 AI-티 점검표(ANTI-TELL)" 반영, version 필드가 있으면 0.8.0으로 맞춘다. 없으면 변경 없이 통과.

- [ ] **Step 7: 검증**

Run: `grep -n '0.8.0' .claude-plugin/plugin.json && grep -n 'ANTI-TELL-CHECKLIST' README.md skills/gx-design/SKILL.md skills/gx-redesign/SKILL.md && grep -c '3종' README.md`
Expected: plugin.json 0.8.0, 세 파일에 ANTI-TELL-CHECKLIST 참조 존재, README '3종' 카운트 0.

- [ ] **Step 8: 커밋**

```bash
git add skills/gx-design/SKILL.md skills/gx-redesign/SKILL.md README.md .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "feat: ANTI-TELL 배달·문서·버전 0.8.0

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: 리뷰 패스 (규격 정합·라이선스·문체)

**Files:**
- Review only (수정은 발견 시): 위 전 파일.

**Interfaces:**
- Consumes: Task 1~5 산출 전부.

- [ ] **Step 1: 리뷰 서브에이전트 1개 스폰**

프롬프트 요지: "브랜치 `feat/selective-adopt-taste-impeccable`의 변경(ANTI-TELL-CHECKLIST.md 신규 + VISUAL-CRAFT·VISUAL-QUALITY·creative-production·creative-review·gx-design SKILL·gx-redesign SKILL·README·plugin.json 보강)을 스펙 `docs/superpowers/specs/2026-07-29-selective-adopt-taste-impeccable-design.md` 대비 검수하라. 확인: (1) MIT·Apache 원문 문장 복붙 없이 재서술인가, (2) 하드 밴이 아니라 '브리프 우선' 프레임인가(체크리스트·detect 게이트 모두), (3) '3대/3종' 잔존 표기 0건·'4대/4종' 정합, (4) 교차 링크(VISUAL-CRAFT↔ANTI-TELL↔VISUAL-QUALITY, production/review의 상대경로) 실재, (5) detect가 설치·훅 없는 선택 게이트로만 서술됐는가, (6) 버전 0.8.0 정합, (7) 기존 문단 훼손·문체 이탈. Critical/Major/Minor로 보고."

- [ ] **Step 2: Critical/Major 수정**

리뷰가 Critical/Major를 내면 해당 파일을 수정하고 그 파일만 재커밋. Minor는 기록만.

- [ ] **Step 3: 최종 확인 커밋(수정 있었을 때만)**

```bash
git add -A && git commit -m "fix: 리뷰 반영 — <요지>

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

- [ ] **Step 4: 완료 보고**

변경 요약(신규 1 + 보강 8, 버전 0.8.0) + 다음 단계(로컬 재설치 검증 또는 PR)를 사용자에게 보고. 릴리즈(태그·PR)는 사용자 요청 시에만.

---

## Self-Review (작성자 체크 결과)

**1. 스펙 커버리지:**
- 신규 ANTI-TELL-CHECKLIST(요소·카피·수치 가드·사용법·브리프 우선) → Task 1 ✓
- VISUAL-CRAFT §1 퍼플 콤보·프리미엄 소비재 신호·팔레트 재사용 금지·링크, §3 Fraunces·Instrument Serif, §6 링크 → Task 2 ✓
- VISUAL-QUALITY 기계 바닥(WCAG·크기·행간·줄길이 등) + detect 선택 게이트(조건·명령·해석·기각·톤 시너지·폴백) → Task 3 ✓
- creative-production 자체 점검 1줄 + creative-review 검수 항·detect 해석 → Task 4 ✓
- 배달(gx-design·gx-redesign SKILL)·README·plugin.json 0.8.0·marketplace → Task 5 ✓
- 실행 방식(리뷰 서브에이전트 1개) → Task 6 ✓
- 스펙의 기각 목록(훅·플레이북·PRODUCT.md·코드 레시피·다이얼 수치화·설치 프롬프트)은 태스크에 없음 = 의도된 제외 ✓

**2. 플레이스홀더 스캔:** 각 편집 스텝에 최종 텍스트 블록 포함. TBD/TODO 없음. plugin.json·marketplace는 "현재값 확인 후 수정"으로 구체화.

**3. 명칭·앵커 정합:** 파일 경로 `skills/gx-design/ANTI-TELL-CHECKLIST.md` 전 태스크 일치. 상대경로 — 동일 디렉터리 링크(`ANTI-TELL-CHECKLIST.md`), 교차 디렉터리(`../gx-design/ANTI-TELL-CHECKLIST.md`) 구분 정확. "Major 이상" 표현 Task 1 §4 = Task 4 Step 2 일치. v0.7 산출 텍스트("위 3대 룩 외에도" 워치리스트 문단, README의 REFERENCE-DRIVEN 등재)를 앵커로 쓰는 스텝은 선행 조건(plugin.json 0.7.0)으로 보호. "3대/3종→4대/4종" 스윕은 파일별 소속 태스크(2·3·4·5)에 분산 배치, 각 태스크 검증에 잔존 카운트 0 확인 포함.
