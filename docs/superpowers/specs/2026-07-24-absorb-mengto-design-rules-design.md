# MengTo/Skills 디자인 규칙 흡수(Absorb MengTo Design Rules) 설계

- **일자**: 2026-07-24
- **대상**: gx-design 제작·검수·프롬프트·시각 크래프트 레이어
- **상태**: 승인됨(B 균형안 채택) — 브랜치 `feat/absorb-mengto-rules`
- **버전 영향**: 0.6.0 → 0.7.0 (사용자향 능력 추가 = minor)

## 목표(한 문장)

디자인 스킬 모음집 [MengTo/Skills](https://github.com/MengTo/Skills)(MIT)에서 **Gemini 웹 생성·전략 파이프라인에 맞는 규칙만 우리 규격으로 흡수**해, 레퍼런스 기반 생성·안티-슬롭·프롬프트 반복 규율·수용 체크를 제작·검수 단계에 심는다. 외부 스킬 런타임 의존 없음(VISUAL-CRAFT가 frontend-design 규칙을 흡수한 것과 동일 패턴).

## 배경 / 결정

- 조사: 3개 병렬 리서치 에이전트가 레포 전량(codex/media/ui/web-design, SKILL.md 90여 개)을 원문 확인.
- **핵심 판정**: 레포의 다수(web-design의 코드 레시피 ~13개, three.js·tailwind·box-shadow 문자열; 에셋 소싱; 일일 영감 캡처 런북)는 **코드 구현/특정 서비스 의존**이라 Gemini 이미지·영상 생성 주 타깃인 우리에게 부적합.
- **흡수 형태 = 규칙 재서술**로 확정(사용자 승인). 이유: (1) MIT 원문 복제는 고지 의무를 유발, 규칙 아이디어 재서술은 라이선스·표절 리스크 없음, (2) 원문은 영어·서구 SaaS·코드 렌더 맥락 → 한국어·Gemini 웹 생성·전략 중심인 우리와 맞지 않아 재서술이 오히려 적합.
- **흡수 범위 = B 균형**으로 확정(사용자 승인): 최대 가치인 레퍼런스 기반 생성 워크플로는 신규 참조 1개로, 나머지 고가치 규칙은 기존 파일에 흡수. 저가치(모션 슈퍼프롬프트·에셋·저작 위생)는 이번 범위 밖(C 포괄에서 다룰 후보).

## 흡수할 규칙 (출처 → 우리 규격)

- **generate-reference-inspired-brand-worlds** (최우선, 우리에 없는 신규 자산):
  - 근접도 다이얼(similarity dial) 30/50/70/85% — 측정점수 아닌 의도 전달, 기본 70(인접 브랜드 패밀리).
  - visual DNA 2-리스트 — 재사용 문법(밀도·팔레트 관계·표면 질감·타입 스케일) ↔ 보호 시그니처(정확 인물·모티프·구도·워드마크 letterform).
  - **저작권 안전 가드레일** — 워드마크·letterform·유명 로고/캐릭터 정확 재현 금지, 원리만 추상화("inspired, not copying").
  - brand matrix / prompt spine — 1레퍼런스 → N브랜드 확장 시 공통 상수 고정 + 브랜드별 변주 + 검증.
- **design-first-ui-prompting**:
  - "variants > rerolls" 반복 규율 — 시스템 1회 고정 후 변형은 한 번에 1변수만.
  - constraints 카드 — FONT/STYLE/MODE 명시값을 프롬프트 앵커로.
  - 2-pass 타이포 — 텍스트 주체 아닌 컷은 오버레이 안전영역을 비워 생성.
  - (9블록 UI 생성 스켈레톤은 이미지 5요소와 목적이 달라 creative-production UX/UI 절의 선택적 참조로만.)
- **web-design 무드 코퍼스(40여 룩)**:
  - "not X, not Y" 부정정의 기법 — 의도한 룩을 가장 가까운 클리셰 2개와 대비해 정의.
  - 명명된 룩 슬롭 워치리스트 — 커뮤니티 수렴 룩(dark-glass-clean·mesh-gradient·clean-minimal-beige·editorial-tech·solar-duotone 등)을 새 디폴트 슬롭 후보로.
  - 룩별 tuning knobs — 특정 룩 선택 시 전용 다이얼을 범용 3다이얼(VARIANCE/MOTION/DENSITY)에 덧붙임.
- **방법론(demo 계약)**:
  - Acceptance checks(수용 체크) — 명세 말미 "이게 맞다고 볼 조건" 체크리스트, 검수 기준으로 사용.

## 아키텍처 — 신규 1 + 보강 4

**신규 `skills/gx-design/REFERENCE-DRIVEN.md`** 하나에 레퍼런스 기반 생성 규칙을 모으고(적용 범위·관계 / 레퍼런스 라벨링 / 근접도 다이얼 / visual DNA 2-리스트 / 저작권 안전 가드레일 / brand matrix / 검수 연계), 나머지는 기존 파일에 외과적으로 흡수한다. 목표 40~55줄, 얇게 유지.

- `VISUAL-CRAFT.md` §1·§2: "not X,not Y" 부정정의 + 명명된 룩 슬롭 워치리스트(§1) + 룩별 tuning knobs 1줄(§2).
- `PROMPT-PLAYBOOK.md`: variants>rerolls 반복 규율(신규 소절) + §2.3 constraints 카드 보강 + §4 2-pass 타이포 1줄 + §2.5에서 `REFERENCE-DRIVEN.md` 상호 링크.
- `creative-production/SKILL.md`: 매체별 필수 섹션에 공통 **수용 체크** 추가 + UX/UI 절에 선택적 UI-프롬프트 스켈레톤 참조.
- `creative-review/SKILL.md`: "제작 가능성" 근처에 수용 체크 충족 여부 1항.

## 저작권 / 라이선스 원칙

- MengTo/Skills = MIT. 재사용 자유이나 원문 "substantial portions" 복제 시 고지 의무.
- 따라서 **모든 흡수는 규칙 재서술** — 스켈레톤·다이얼 등 구조 포맷은 필드 구성만 참고하고 문구는 한국어·Gemini 맥락으로 새로 쓴다. 원문 문장 복붙 금지.
- 아이러니 방지: 우리가 흡수하는 저작권 가드레일(레퍼런스 letterform 재현 금지)을, 이 흡수 작업 자체에도 적용한다.

## 톤 기준·안티-슬롭과의 관계

- 디자인 톤 기준([[DESIGN-TONE-ANCHOR]])이 있으면 **톤 기준이 상위** — 근접도 다이얼·visual DNA는 톤 기준 안에서 정한다.
- 레퍼런스(타인 자산)와 디자인 톤 기준(자기 브랜드)은 다른 축: 톤 기준 = 구속(재현 대상), 레퍼런스 = 저작권 가드 대상(재현 금지). `REFERENCE-DRIVEN.md`가 이 구분을 명시.
- 근접도 다이얼은 VISUAL-CRAFT 톤 다이얼의 형제(브랜드 톤 강도 × 레퍼런스 근접도) — 승인된 전략에 종속된 실행 보조로만 쓴다.

## 변경 파일

1. 신규 `skills/gx-design/REFERENCE-DRIVEN.md`
2. `skills/gx-design/VISUAL-CRAFT.md` — §1 부정정의·룩 워치리스트, §2 룩별 다이얼
3. `skills/gx-design/PROMPT-PLAYBOOK.md` — variants>rerolls, constraints 카드, 2-pass, REFERENCE-DRIVEN 링크
4. `skills/creative-production/SKILL.md` — 수용 체크 표준 섹션, UI 스켈레톤 선택 참조
5. `skills/creative-review/SKILL.md` — 수용 체크 충족 여부 검수 항
6. `skills/gx-design/SKILL.md` — 단계 3(Production) 위임 프롬프트에 REFERENCE-DRIVEN.md 경로 배달(레퍼런스 입력이 있을 때)
7. `README.md` — 구성 문단에 REFERENCE-DRIVEN 등재 + FAQ "AI 티"에 저작권 가드 한 줄 + 버전
8. `.claude-plugin/plugin.json` — 0.6.0 → 0.7.0
9. `.claude-plugin/marketplace.json` — 소개 반영(해당 시)

## 비목표(YAGNI)

- 코드 레시피(three.js·tailwind·box-shadow 등)·에셋 소싱(unsplash/aura)·일일 영감 캡처 런북·HTML→프롬프트는 흡수하지 않는다(Gemini 부적합·서비스 의존·노후화).
- video-to-superprompt 모션 템플릿(#6)·references-beat-paragraphs·저작 위생 규칙(#7)은 이번 범위 밖(C 포괄 후보).
- 외부 스킬을 런타임 의존으로 연결하지 않는다(설치 요구 없음).
- 프로그램식 린터/검증기 도입 없음.

## 실행 방식

변경 9건이 `REFERENCE-DRIVEN.md` 계약과 기존 파일 교차 참조를 공유하므로 인라인 구현 후 리뷰 서브에이전트 1개로 검수(visual-craft·톤 기준 작업과 동일 판단). 구현 계획은 `docs/superpowers/plans/`에 별도 작성.
