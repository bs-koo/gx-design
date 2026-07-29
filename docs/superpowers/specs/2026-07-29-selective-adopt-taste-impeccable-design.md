# taste·impeccable 선택 도입(Selective Adoption) 설계

- **일자**: 2026-07-29
- **대상**: gx-design 시각 크래프트·품질 루프·제작·검수 레이어
- **상태**: 승인됨 — 브랜치 `feat/selective-adopt-taste-impeccable`(v0.7 머지 후 main에서 분기)
- **버전 영향**: 0.7.0 → 0.8.0 (사용자향 품질 능력 추가 = minor)
- **선행 조건**: v0.7(MengTo 흡수, `feat/absorb-mengto-rules`) 구현·머지 후 착수 — 양쪽이 VISUAL-CRAFT §1을 만지므로 순서 고정

## 목표(한 문장)

taste-skill(Leonxlnx, MIT)·impeccable(pbakaus, Apache 2.0)에서 **결과물 품질을 실제로 올리는 규칙만 선택 재서술**하고, impeccable의 detect CLI를 **가용 시 선택 게이트**로 연결해, 요소 레벨 AI-티 제거와 기계 검증 바닥을 제작·검수에 심는다. 통째 흡수·런타임 의존·훅 설치 없음.

## 배경 / 결정

- 조사: 병렬 리서치 에이전트 2개가 두 저장소 원문 전량 확인(taste SKILL.md v2 1,215줄, impeccable 탐지 레지스트리 60규칙 = slop 33 + quality 27).
- **판정 1 — impeccable은 린터가 아니라 경쟁 파이프라인**(플레이북 35+, 서브에이전트 4, PostToolUse/Stop 훅). 시스템 도입 시 gx-design의 전략→제작→검수와 역할 중복 + 훅이 "브리프 우선" 원칙과 충돌. → 시스템 도입 기각, 규칙과 CLI만 취함.
- **판정 2 — taste는 v0.6에서 다이얼·일관성 잠금만 흡수**했고, 구체 수치·금지 목록 델타가 크게 남아 있음.
- **사용자 결정: 통째 흡수 대신 선택 도입.** 선별 기준 3개 — (1) 우리 레그(Gemini 웹 생성 프롬프트 패키지·코드 렌더)에 적용 가능, (2) 기존 규격이 못 잡는 델타, (3) 유행이 아닌 내구성 있는 규칙.

## 도입 항목 (출처 → 우리 규격)

### A. 신규 `skills/gx-design/ANTI-TELL-CHECKLIST.md` — 요소·카피·구조 텔 카탈로그

VISUAL-CRAFT §1(3대 기본 룩)이 못 잡는 **요소 레벨** AI-티를 제작 자체 점검 + 검수 입력으로 쓰는 얇은 체크리스트(목표 60~80줄). 전 항목 재서술, 원문 복제 금지.

1. **요소 레벨 시각 텔** (impeccable slop 재서술, 매체 공통):
   - side-tab 액센트 보더(카드 한쪽 두꺼운 색 테두리 — "가장 대표적 AI-UI 표식")
   - 그래디언트 텍스트 / 글로우 그림자·radial halo·스포트라이트 배경(다크 글로우 계열 통합)
   - 카드 안의 카드(nested cards) / 단조로운 등간격 spacing(리듬 부재)
   - 제목 위 아이콘 타일 / hero eyebrow 칩·kicker 라벨
   - 가짜 생동감 3종 — 펄싱 상태 점·장식용 깜빡이 커서·자동 스크롤 마퀴(기본 금지, 마퀴 예외 시 페이지당 1)
   - 타이포 텔 — 이탤릭 세리프 디스플레이·과대 h1·과압축 자간
   - 도형 조립 일러스트(자리표시자 클립아트)
   - 동일 카드 3개 그리드(taste) / 지그재그 스플릿 연속 3개 이상(taste)
2. **카피·콘텐츠 텔** (taste §9 + impeccable 카피 규칙, 한국어 등가 재서술):
   - "Jane Doe 효과" — 제네릭 이름(John Doe·홍길동)·제네릭 아바타·완벽한 숫자(99.99%)·슬롭 브랜드명(Acme·Nexus류)
   - 필러 동사·buzzword — 영문 Elevate/Seamless/Unleash/streamline류 + 한국어 등가("혁신적인"·"획기적인" 남용)
   - 짧은 대조 반복 어투(aphoristic cadence) / em-dash 과다(**영문 산출물 카피 한정** — 한국어 문장부호 관습에는 미적용)
   - 가짜 캡션·버전 라벨(BETA·V0.6)·스크롤 큐("↓ scroll")·로케일/날씨 스트립
   - div로 만든 가짜 스크린샷·대시보드 금지 — 실제 렌더·생성 이미지·실제 컴포넌트만
3. **구조 수치 가드** (taste, 웹/UI 산출물 한정):
   - 히어로 텍스트 요소 최대 4(eyebrow·headline·subtext·CTA), 서브텍스트 짧게(영문 ~20단어 등가), CTA는 첫 뷰포트 안
   - eyebrow 라벨은 3섹션당 최대 1(taste 자칭 "가장 많이 위반되는 규칙 1위")
   - 데스크톱 네비 한 줄 유지
4. **사용법 절**: 제작 완료 전 자체 점검 → 검수 입력 → detect 게이트(아래 C)와의 관계. **모든 항목은 "무심코 기본값" 금지이지 하드 밴이 아님 — 브리프가 요구하면 브리프가 이긴다**(VISUAL-CRAFT §1과 동일 프레임).

### B. 기존 파일 외과 보강

- **VISUAL-CRAFT.md**:
  - §1: **AI 퍼플/시안 콤보를 4번째 기본 룩 신호로 추가**(현재 3대 룩에 빠져 있는 가장 유명한 텔) + 프리미엄 소비재 팔레트의 구체 신호(크림·브라스·옥스블러드·에스프레소 계열) 1줄 + "같은 레포 직전 산출물과 무근거 동일 팔레트 금지"(taste 로테이션 규칙의 우리식 재서술) + ANTI-TELL-CHECKLIST 링크.
  - §3: 금지 폰트 구체화 — Inter·Roboto·Arial에 **Fraunces·Instrument Serif**(LLM 애용 디스플레이 세리프) 추가, "크리에이티브하니까 세리프"라는 기본값 판단 금지(세리프는 브리프·장르가 요구할 때만).
  - §6: 콘텐츠 텔 요약 1줄 + 체크리스트 링크.
- **VISUAL-QUALITY.md**:
  - 비평 기준에 **기계 바닥 점검** 소절 추가(impeccable quality 규칙 재서술): WCAG AA 대비(4.5:1/3:1)·본문 최소 크기(≥14px)·line-height(본문 ≥1.4)·줄 길이 상한·스킵 헤딩·회색-on-컬러·오버플로/가림. 한글 산출물은 줄 길이 등 등가 기준으로 조정 명시.
  - **detect 선택 게이트** 추가(아래 C).
- **creative-production/SKILL.md**: 제작 완료 전 ANTI-TELL-CHECKLIST 자체 점검 1줄(v0.7 수용 체크와 나란히).
- **creative-review/SKILL.md**: 시각 완성도 절에 체크리스트 준수 검수 항 1개 + detect 출력이 첨부된 경우의 해석 규칙.

### C. detect 선택 게이트 (Playwright MCP 선례와 동일 패턴)

- **실행 조건**: 코드 렌더 산출물(HTML/CSS)이고 node·npx 가용할 때만. 미가용이면 ANTI-TELL-CHECKLIST 수동 점검 폴백 — **새 하드 의존 없음**.
- **실행 형태**: `npx --yes impeccable@latest detect <렌더 폴더>` 1회 실행. **스킬·훅 설치가 아니다**(impeccable의 .claude 설치·PostToolUse/Stop 훅은 도입하지 않음 — 훅이 세션 전체에 자기 규칙을 주입해 브리프 우선 원칙과 충돌).
- **결과 해석**: error(스크립트 오류·콘텐츠 비가시 등) = 검수 Critical 상당 / 기본 = 비평 대상 / advisory = 참고. 출력 전문을 렌더 품질 로그에 첨부.
- **기계 출력은 입력이지 판정자가 아님**: detect가 브리프가 의도한 선택(예: 브리프가 요구한 크림 팔레트)을 지적하면 브리프 우선으로 기각하고 기각 사유를 로그에 남긴다.
- **톤 기준 시너지**: DESIGN.md 톤 기준이 있으면 detect의 design-system-* 규칙(폰트·색·radius·타입 스케일 이탈)이 DESIGN-TONE-ANCHOR 준수를 기계 검사해 줌 — 검수 축 A의 보조 입력.

## 도입하지 않는 것 (명시 기각)

- **impeccable**: 훅(PostToolUse/Stop)·서브에이전트 4개·플레이북 35+(init/critique/audit/polish…)·PRODUCT.md 워크플로 — 우리 파이프라인과 역할 중복. DESIGN.md `document` 워크플로 — DESIGN-TONE-ANCHOR가 같은 포맷(Google Labs)을 이미 규정.
- **taste**: Tailwind 클래스·Motion/GSAP 코드 스켈레톤·디자인 시스템 설치 명령(코드 스택 의존 — MengTo 때와 동일 사유) / 브리프→디자인시스템 매핑 표(Fluent·Carbon 등, 코드 렌더 스택 전용) / 다이얼 1~10 수치화(기존 정성 다이얼과 규격 이중화) / 하드 밴 프레임(세리프 금지·em-dash 전면 금지 등은 "무심코 기본값 금지"로 완화 재서술) / Pre-Flight 별도 체크리스트 기구(v0.7 수용 체크와 중복 — 항목만 ANTI-TELL로 합류).
- **노션 가이드의 설치 프롬프트**: 운영 런북 성격이라 디자인 규격에 넣지 않음 — detect 게이트 절의 실행 명령 두 줄로 충분.

## 라이선스 원칙

taste = MIT, impeccable = Apache 2.0. 모든 도입은 **규칙 아이디어의 한국어 재서술** — 원문 문장·표 복제 금지(고지 의무 회피 + 우리 맥락 적합화). MengTo 흡수와 동일 원칙.

## 변경 파일

1. 신규 `skills/gx-design/ANTI-TELL-CHECKLIST.md`
2. `skills/gx-design/VISUAL-CRAFT.md` — §1 퍼플 콤보·팔레트 신호·링크, §3 폰트 밴, §6 링크
3. `skills/gx-design/VISUAL-QUALITY.md` — 기계 바닥 점검 + detect 선택 게이트
4. `skills/creative-production/SKILL.md` — 자체 점검 1줄
5. `skills/creative-review/SKILL.md` — 체크리스트 검수 항 + detect 해석
6. `skills/gx-design/SKILL.md` · `skills/gx-redesign/SKILL.md` — 제작·검수 위임 프롬프트에 ANTI-TELL-CHECKLIST.md 경로 배달(기존 VISUAL-CRAFT 배달과 동일 관례)
7. `README.md` — 구성 목록·버전
8. `.claude-plugin/plugin.json` — 0.7.0 → 0.8.0
9. `.claude-plugin/marketplace.json` — 소개 반영(해당 시)

## 비목표(YAGNI)

- 자체 린터/검출기 구현 없음(기성 CLI를 가용 시 빌려 쓸 뿐).
- 두 스킬을 런타임 의존·설치 요구로 연결하지 않음.
- Gemini 프롬프트 규격(PROMPT-PLAYBOOK)·전략 레이어는 건드리지 않음(v0.7 범위와 중복 회피).

## 원자료

- taste SKILL.md v2 전문: 세션 스크래치패드 `taste-skill-v2-full.txt` (원본: github.com/Leonxlnx/taste-skill `skills/taste-skill/SKILL.md`)
- impeccable 60규칙 표: 세션 스크래치패드 `impeccable-rules-60.md` (원본: github.com/pbakaus/impeccable `.claude/skills/impeccable/scripts/detector/registry/antipatterns.mjs`)
- 스크래치패드는 세션 종속 — 구현 세션이 다르면 원본 URL에서 재확보.

## 실행 방식

변경 9건이 ANTI-TELL-CHECKLIST.md 계약을 공유하므로 v0.6·v0.7과 동일하게 인라인 구현 후 리뷰 서브에이전트 1개로 검수. 구현 계획은 승인 후 `docs/superpowers/plans/`에 별도 작성.
