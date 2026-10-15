# gx-design v0.11 — 모션(UI·영상) 흡수 · 사용자 입력 가이드 · 점검 전용 모드

- 날짜: 2026-10-15
- 기준: origin/main 2be3a81 (plugin 0.10.0) → 목표 0.11.0
- 계기: 국내 가이드 슬라이드 "디자인 스킬 5개 + 이렇게 시키세요 + 마스터 프롬프트"(DESIGN.md · taste · impeccable · emil-design-eng · Playwright MCP)

## 1. 결정 사항 (사용자 확정)

1. **점검 전용은 gx-redesign의 모드**로 둔다 — 점검 후 "여기서 끝 / 이어서 리디자인" 게이트로 단계 3에 합류(진단 재실행 없음).
2. **high-end-visual-design은 선택형 프리셋**으로 흡수 — 브리프가 프리미엄·럭셔리·하이엔드를 요구할 때만.
3. **다이얼은 따로 묻지 않고 전략안 미리보기에 표기** — 안 선택 = 다이얼 확정.
4. **영상·모션 그래픽 보강** — UI 모션(emil)과 영상 모션 규칙을 분리.

원칙(v0.6 이래 불변): 외부 스킬은 **규칙만 우리 문장으로 흡수**하고 런타임 의존 0. 설치돼 있으면 쓰는 "선택 의존"만 허용(DESIGN-INTELLIGENCE 선례). 게이트 3개(브리프·전략·실물) 불변. 디자인 톤 기준이 VISUAL-CRAFT·MOTION보다 상위.

호스트 호환 제약(tests/test_codex_compat.py): 활성 스킬 본문에 `AskUserQuestion`·`multiSelect`·`preview를 쓴다`·`WebSearch` 문자열 금지. 질문은 [HOST-COMPAT.md]의 "질문·선택"으로 지칭하고, 복수 선택·시각 미리보기는 "호스트가 지원하면"으로 쓴다. 서브에이전트 이름·모델 고정·필수 위임 문장 금지.

## 2. 외부 소스 요지 (2026-10-15 조사)

| 소스 | 라이선스 | 흡수 대상 |
|---|---|---|
| emilkowalski/skills `emil-design-eng` | MIT | 빈도 규칙, 이징 곡선, 지속시간 표, press·hover, 진입 스케일, transform-origin, reduced-motion, 금지 목록, Before/After/Why 출력 |
| Leonxlnx/taste-skill `taste-skill-v2-experimental` | MIT | 3다이얼 1~10 레벨 정의. **주의: 2026-10-13 v2.0.0부터 기본 `design-taste-frontend`는 다이얼 없음** — 출처를 v2-experimental로 명기 |
| Leonxlnx/taste-skill `high-end-visual-design`(soft-skill) | MIT | 프리미엄 프리셋(Double-Bezel 카드, pill 버튼, 헤어라인·ambient shadow, 초경량 라인 아이콘, 넓은 섹션 여백, 플로팅 내비) |
| pbakaus/impeccable audit/polish/detect | Apache-2.0 | audit(읽기 전용)·polish(수정) 명명, P0~P3 대응표, detect 최신 사양(URL 대상, 종료코드 0/2/1, `--json`) |
| microsoft/playwright-mcp | Apache-2.0 | 여정 시나리오, 375×812·데스크톱, snapshot(조작)/screenshot(시각) 구분, 콘솔 오류, 설치 명령 1회 안내 |
| VoltAgent/awesome-design-md | MIT | DESIGN.md 9절 포맷 매핑, 카탈로그 안내 |
| Remotion `remotion-best-practices` | — | 설치 시 선택 의존으로만 언급(경로·구조 미확인 — 규칙 인용 금지) |

## 3. 변경 설계

### 3.1 `skills/gx-design/MOTION.md` (신설)

- **§0 적용 범위 분기**: §A = UI 인터랙션(웹·앱 화면, 코드 렌더 화면), §B = 모션 그래픽·영상(Remotion·FFmpeg 렌더, 편집 핸드오프, Veo 프롬프트의 모션 서술). **§A 규칙을 영상에 적용하지 않는다**(예: 300ms 상한은 영상에 무의미).
- **§A UI 인터랙션** (emil-design-eng 흡수)
  - A1 빈도 규칙 표: 하루 100회+(단축키·커맨드 팔레트) 없음 / 하루 수십 회(hover·리스트 이동) 제거·축소 / 가끔(모달·드로어·토스트) 표준 / 드묾·첫 사용(온보딩·완료 축하) 연출 허용. 키보드로 시작한 동작은 애니메이션하지 않는다. 모든 모션은 목적(공간 연속성·상태 표시·설명·피드백·갑작스런 등장 방지) 중 하나를 가진다.
  - A2 이징: 진입 ease-out(기본), 화면 내 이동 ease-in-out, hover·색 ease, 등속(마퀴·진행바) linear. UI에 ease-in 금지. 곡선: 강한 ease-out `cubic-bezier(0.23, 1, 0.32, 1)`, 강한 ease-in-out `cubic-bezier(0.77, 0, 0.175, 1)`, 드로어 `cubic-bezier(0.32, 0.72, 0, 1)`.
  - A3 지속시간 표: press 100–160ms / 툴팁·작은 팝오버 125–200ms / 드롭다운 150–250ms / 모달·드로어 200–500ms. **UI 인터랙션은 300ms 이하가 기본, 모달·드로어와 마케팅 연출만 예외**. 나가는 모션은 들어오는 모션보다 짧게.
  - A4 press·hover: 누를 수 있는 요소 `:active`에 `scale(0.97)`(0.95–0.98), `transition: transform 160ms ease-out`. hover 효과는 `@media (hover: hover) and (pointer: fine)` 안에서만.
  - A5 진입: `scale(0)` 시작 금지 — `scale(0.9)` 이상 + `opacity: 0`. 팝오버는 트리거 쪽 transform-origin(모달만 center).
  - A6 금지: `transition: all`, width·height·padding·margin 애니메이션(transform·opacity만), 빠르게 반복 발동되는 요소의 keyframes(중단 가능한 transition 사용), stagger 항목 간 80ms 초과·stagger가 인터랙션을 막는 것.
  - A7 스프링: 드래그 모멘텀·중단 가능한 제스처에만. bounce 0.1–0.3, 기능성 데이터 표시(차트·잔액)에는 쓰지 않는다.
  - A8 reduced-motion: "0이 아니라 덜" — opacity·색 전환은 유지, 이동·확대·패럴랙스 제거.
- **§B 모션 그래픽·영상** (신설, gx-design 자체 규칙)
  - B1 시간 단위는 프레임: fps(24/30/60)를 명세에 고정, 씬 길이를 `초(프레임)`로 병기, 씬 합 = 러닝타임을 프레임 단위로 검산.
  - B2 가독 시간: 화면 텍스트는 등장 연출이 끝난 뒤 정지 홀드를 둔다. 홀드 길이는 "소리 내어 두 번 읽을 수 있는 시간"을 기본으로 하고, 명세에 텍스트별 홀드 초를 적는다(고정 수치 규칙은 두지 않는다 — 출처 미확정).
  - B3 이징 어휘(UI와 별도): 진입 감속, 퇴장 가속 허용, 강조 오버슈트 허용, 등속(티커·롤링). 같은 역할의 모션은 같은 곡선.
  - B4 전환: 한 영상의 전환 종류(컷·디졸브·매치컷·마스크·푸시)는 2~3종으로 제한하고 역할을 정한다(예: 챕터 = 마스크, 씬 내 = 컷).
  - B5 훅과 리듬: 첫 1~3초에 핵심 메시지 또는 시각 사건. BGM이 있으면 비트 기준 컷 포인트를 명세에 적는다.
  - B6 플랫폼 안전영역: 세로형 숏폼(Reels·Shorts·TikTok)은 상하단·우측 UI 영역에 자막·CTA·로고를 두지 않는다. 게시 플랫폼을 명세에 적고 안전영역 가이드를 렌더 확인에 쓴다.
  - B7 절제: VISUAL-CRAFT §5를 시간축에 적용 — 시그니처 모션 1개, 나머지는 조용히.
  - B8 코드 렌더 도구: Remotion(설치돼 있고 공식 Remotion 스킬이 호스트에 있으면 그 지침을 선택 참조)·FFmpeg. 없으면 설치를 강제하지 않고 PRODUCTION-HANDOFF의 다른 경로를 안내.
- **§C 모션 점검 출력 형식**: 이슈당 1행 표 `요소·위치 | Before | After | Why`. "Before:/After:" 줄 나열 금지. gx-redesign 제작 기록(before → after → 근거)과 같은 축.
- **출처** 절: emil-design-eng(MIT) 재서술 고지, §B는 자체 규칙.

### 3.2 `VISUAL-CRAFT.md`

- §2 다이얼을 1~10 레벨로 정의(v2-experimental 기준 재서술):
  - VARIANCE 1–3 대칭 그리드·중앙 정렬 / 4–7 약한 겹침·혼합 비율·좌정렬 헤더 / 8–10 비대칭·분수 컬럼·의도적 큰 여백. 4 이상은 좁은 화면에서 단일 컬럼으로 접힌다.
  - MOTION 1–3 자동 모션 없음, hover·press 피드백만 / 4–7 속성 명시 transition·공통 이징·로드 stagger / 8–10 스크롤 연동 reveal·패럴랙스(스크롤 이벤트 직접 구독 대신 관찰자 API).
  - DENSITY 1–3 갤러리급 여백 / 4–7 일반 앱 간격 / 8–10 콕핏(촘촘한 패딩, 박스 대신 1px 구분선, 숫자 고정폭).
  - 기본값은 고정하지 않는다 — UI-QUALITY §1 화면 목적에서 도출(설득 ↑VARIANCE, 업무 수행 ↑DENSITY·↓MOTION, 읽기 ↓DENSITY, 감상 ↓DENSITY·콘텐츠 우선).
  - **다이얼은 사용자에게 숫자로 묻지 않는다** — 전략안마다 값을 제시하고, 안 선택으로 확정(DESIGN-IT-TWICE).
- §4 모션은 요약 3줄 + [MOTION.md] 링크로 대체(§A/§B 분기 명시).
- §7 신설 "프리미엄 프리셋(선택)": 발동 조건 = 브리프·톤 기준이 프리미엄·럭셔리·하이엔드를 명시. 내용 = Double-Bezel 카드(바깥 셸 반투명·헤어라인·작은 패딩 + 안쪽 코어 동심 radius), pill 버튼과 원 안 화살표, 1px 회색 테두리·진한 drop shadow 대신 헤어라인 링·은은한 ambient shadow, 굵은 stroke 아이콘 대신 초경량 라인 아이콘, 표준의 약 2배 섹션 여백, 화면 상단에 붙은 내비 대신 떠 있는 내비, 768px 미만 단일 컬럼. **충돌 해소**: 프리셋의 긴 모션(~700ms)은 마케팅 스크롤 연출에만, UI 인터랙션은 MOTION §A3 우선. 글래스 연출은 §1 워치리스트(dark-glass-clean)와 겹치므로 "not X, not Y" 부정 정의로 못박는다. 톤 기준이 있으면 그 안에서만.

### 3.3 `VISUAL-QUALITY.md`

- 수정 회차를 **polish 패스**로 명명(진단 = audit, 읽기 전용 / 수정 회차 = polish). 심각도 대응표: P0 ≈ Critical(과업 차단), P1 ≈ Critical/Major(접근성 실패), P2 ≈ Major, P3 ≈ Minor — gx 체계 유지.
- 크래프트 비평 항목의 모션 줄을 MOTION §A로 연결.
- **여정 시나리오**: 브리프·개선 브리프의 `핵심 여정`(예: 메인 → 상세 → 장바구니)을 모바일(375×812)·데스크톱 대표 폭에서 실제 클릭으로 따라간다. Playwright MCP가 가용하면 조작은 접근성 스냅샷 기준, 스크린샷은 시각 확인용으로 구분하고 콘솔 오류를 수집해 실행 검증 로그에 남긴다.
- **Playwright 미가용 안내**: UI 코드 산출물인데 브라우저 자동화가 없으면 폴백하되, 설치 방법(Claude Code: `claude mcp add playwright npx @playwright/mcp@latest`, Codex: 호스트의 MCP 설정 방법)을 **세션당 1회** 안내한다. 자동 설치 금지.
- **detect 최신화**: 대상에 렌더 폴더 또는 로컬 URL. 종료코드 0 = 발견 없음, 2 = 발견, 1 = 스캔 실패(검증 제약). 필요 시 `--json`.
- **영상 분기**: 영상·모션 그래픽은 스틸 2~3장 대신 (1) 컨택트 시트(씬마다 시작·중간·끝 프레임) + (2) 핵심 구간 저해상도 프리뷰를 비평. 항목: B1 프레임 검산, B2 가독 홀드, B4 전환 일관, B5 첫 1~3초, B6 안전영역, 루프 지점(있으면).

### 3.4 제작·검수 배달

- `creative-production/SKILL.md`: 영상 필수 섹션에 `fps·규격·게시 플랫폼 / 씬별 초(프레임) 검산 / 텍스트 홀드 / 전환 체계 / 시그니처 모션` 추가. UX/UI 필수 섹션에 `모션 명세(MOTION §A — 요소·트리거·지속시간·이징)`(모션이 있을 때). 제작 원칙에 MOTION.md 참조. 수용 체크에 영상 항목(안전영역·프레임 합) 추가.
- `creative-review/SKILL.md`: 모션 줄을 MOTION §A로 교체(빈도·ease-in 금지·300ms·reduced-motion "덜"). 영상 절에 B1·B2·B5·B6 확인 가능 항목 추가. 모션 지적은 §C 표로.
- `REVIEW-AXES.md`: 축 B 입력에 모션이 있는 산출물이면 MOTION.md 전달.
- `agents/creative-producer.md`: 모션·영상 제작 시 MOTION.md 준수 한 줄(Claude 전용 파일 — 기존 서술 톤 유지).

### 3.5 오케스트레이터·인터뷰 (사용자 입력 가이드 — 안쪽 층)

- **요청 해석 카드** (`BRIEF-INTERVIEW.md` §4 머리, `REDESIGN-INTERVIEW.md` 준용): 첫 라운드 전에 한 줄 요청을 슬롯 `무엇 / 누구·목적 / 피할 것 / 기준 자료(DESIGN.md·레퍼런스) / 범위·기기`로 펼쳐 채워진 칸 ✓·빈 칸 ?로 3~5줄 보여 준다. 질문이 아니라 머리말이며 문항 예산에 포함하지 않는다. 빈 칸 중 결정 트리의 frontier에 있는 것만 묻는다. "요청을 다시 써 달라"고 되돌려보내지 않는다.
- **"피할 것" 문항** (중류): 하류 스타일 선택이 아니라 제약 질문. 옵션은 VISUAL-CRAFT §1 기본 룩(크림+세리프 / 다크+형광 / AI 보라 그라데이션 / 중앙 정렬 히어로 등)에서 매체에 맞는 3~4개, 복수 선택 가능함을 밝히고, 호스트가 시각 미리보기를 지원하면 각 룩의 간단한 레이아웃 스케치를 준다. 사용자가 요청에 "X 말고"를 이미 썼으면 묻지 않는다.
- **톤 기준 문항 확장**: "없음" 선택지 설명에 DESIGN.md 고르는 곳(designmd.co, awesome-design-md)을 적는다.
- **핵심 여정** (UX/UI): 브리프 양식에 `핵심 여정(검증 시나리오)` 항목 추가 — 자료로 알 수 있으면 직접 기록, 모르면 화면 목적 질문과 함께 묻는다.
- **DESIGN-IT-TWICE / gx-redesign 단계 3**: 각 안에 `다이얼 VARIANCE·MOTION·DENSITY 값 + 한 줄 근거`를 포함하고, 선택지 미리보기(호스트 지원 시) 또는 선택지 설명에 표기. 같은 게이트에 **모션 범위** 문항을 붙인다(모션 있는 산출물일 때만): UI = 피드백만 / 진입 연출 / 스크롤 연출, 영상 = 정적+컷 편집 / 키네틱 타이포 / 풀 모션 그래픽. 첫 옵션은 화면 목적 기반 추천.
- **design-strategy/SKILL.md** 콘셉트 형식에 다이얼 값·모션 범위 필드 추가.
- **PRODUCTION-HANDOFF.md**: 영상 코드 렌더 선택 시 fps·게시 플랫폼을 확인(브리프에 있으면 생략). UI 프로토타입·코드 렌더 선택 시 `검증 여정` 확인(브리프의 핵심 여정 재사용, 없으면 묻는다).
- **DESIGN-TONE-ANCHOR.md**: §1 허용 포맷에 awesome-design-md 9절 포맷 매핑(Visual Theme & Atmosphere→톤 키워드, Color Palette & Roles→팔레트, Typography Rules→타이포, Component Stylings·Depth & Elevation·Layout Principles→형태, Do's and Don'ts→금지, Responsive Behavior→반응형, Agent Prompt Guide→제작 프롬프트 참고). §3 안내에 awesome-design-md 추가. 타 사이트 DESIGN.md는 soft 기본 + REFERENCE-DRIVEN 저작권 가드.

### 3.6 gx-redesign 점검 전용 모드

- 모드 결정에 세 번째 축 **범위**: 인자에 "점검"·"감사"·"audit"·"점검만"이 있거나 요청이 점검·테스트만 요구하면 **점검 전용**. 진행 모드(전체/핵심)와 별개 축이다.
- 흐름: 단계 0 자산 인벤토리(전수) + **경량 개선 브리프**(점검 대상: 시각·UX / 모션 / AI 티 / 실행 여정 중 복수, 대상 화면·URL, 기기 — 1라운드) → 승인 → 단계 1 진단(기존 규칙 그대로, 모션 대상이면 MOTION.md, 여정 대상이면 VISUAL-QUALITY 여정 시나리오) → 진단 보고(모션은 §C 표, 그 외는 기존 진단표) → **이어가기 게이트**: 여기서 종료 / 이어서 리디자인(단계 2 또는 3으로 합류, 진단 재사용) / 지적 항목만 바로 수정(polish — 최소 개입 A안으로 간주해 단계 4 제작→단계 5 검수, 전략 선택 게이트는 이 선택으로 갈음했음을 기록).
- 게이트 원칙: 브리프 승인 게이트는 경량화하되 유지. 수정은 이어가기 게이트 선택 후에만.

### 3.7 사용자 입력 가이드 — 바깥 층 (README · site)

- README에 `## 이렇게 시키세요` 절: 요청 공식 **[무엇을] + [누구·목적] + [뻔한 X 말고 Y처럼] + [기준 자료: DESIGN.md·레퍼런스] + [범위·기기]**, 예시 카드(신규 UI / 점검 전용 모션 / 여정 테스트 / BX / 숏폼 영상) — Claude Code 슬래시와 Codex `$` 표기 병기.
- README에 `### 디자인 스킬 5개를 따로 설치하지 않아도` 대응표: DESIGN.md → 단계 0 톤 기준 / taste → 전략 다이얼 / impeccable audit·polish → 진단·품질 루프 / emil → MOTION §A / Playwright → 여정 검증(가용 시). 각 출처·라이선스 링크.
- README 구성 표·참조 파일 목록에 MOTION.md 추가. 진행 모드 절에 점검 전용 추가.
- site/index.html: "이렇게 시키세요" 섹션(공식 + 예시 3~5개, 기존 디자인 토큰·호스트 토글 패턴 재사용). 기존 테스트가 검사하는 설치 블록·before/after 카드 구조 보존.

### 3.8 버전·테스트

- `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json`(버전 필드가 있으면) → 0.11.0.
- `tests/test_motion_guide_audit_mode.py` 신설 — 아래 앵커 문자열 존재 검사 + MOTION.md 링크 배달 검사 + 금지 문자열 비존재.

## 4. 필수 앵커 문자열 (구현·테스트 공통 계약)

| 파일 | 반드시 포함 |
|---|---|
| skills/gx-design/MOTION.md | `## A. UI 인터랙션`, `## B. 모션 그래픽·영상`, `## C. 모션 점검 출력`, `cubic-bezier(0.23, 1, 0.32, 1)`, `scale(0.97)`, `(hover: hover) and (pointer: fine)`, `ease-in`, `프레임`, `안전영역`, `Before | After | Why` |
| skills/gx-design/VISUAL-CRAFT.md | `MOTION.md`, `1–3`, `8–10`, `프리미엄 프리셋` |
| skills/gx-design/VISUAL-QUALITY.md | `polish`, `핵심 여정`, `컨택트 시트`, `@playwright/mcp@latest` |
| skills/gx-design/BRIEF-INTERVIEW.md | `요청 해석 카드`, `피할 것`, `핵심 여정` |
| skills/gx-design/DESIGN-IT-TWICE.md | `다이얼`, `모션 범위` |
| skills/gx-redesign/SKILL.md | `점검 전용`, `이어가기 게이트`, `MOTION.md` |
| skills/gx-design/DESIGN-TONE-ANCHOR.md | `awesome-design-md` |
| skills/creative-production/SKILL.md | `MOTION.md`, `fps` |
| skills/creative-review/SKILL.md | `MOTION.md` |
| README.md | `## 이렇게 시키세요`, `MOTION.md`, `점검 전용` |

금지(활성 스킬 전체): `AskUserQuestion`, `multiSelect`, `preview를 쓴다`, `WebSearch`, 서브에이전트 이름·모델 고정.

## 5. 검증

1. `python -m unittest discover -s tests -v` 전부 통과.
2. Codex 교차 검토(읽기 전용): (a) 변경 diff 코드리뷰, (b) Codex 호스트에서의 동작 점검(스킬 발견·질문 폴백·위임 폴백·링크·도구 가정) + Codex 사용성 개선안.
3. 검토 결과 반영 후 재검증.
