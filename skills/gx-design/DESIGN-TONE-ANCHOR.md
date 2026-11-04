# DESIGN-TONE-ANCHOR — 디자인 톤 기준 파일 처리 규격

사용자가 첨부한 디자인 시스템 파일을 "톤 기준"으로 받아 전략→제작→검수에 물리는 규칙.
gx-design·gx-redesign 두 오케스트레이터가 공통으로 참조한다(gx-redesign은 `../gx-design/DESIGN-TONE-ANCHOR.md`).

## 1. 톤 기준이란

- **정의**: 팔레트·타이포그래피·톤·형태(radius·spacing) 규칙을 담은, 사용자가 첨부하거나 프로젝트에 이미 있는 디자인 시스템 문서.
- **1순위 포맷**: `DESIGN.md` (Google Labs 포맷 — YAML frontmatter 토큰 + 마크다운 근거. 절: Overview / Colors / Typography / Layout·Spacing / Elevation / Shapes / Components / Do's·Don'ts). designmd.co는 이 포맷의 기성 카탈로그다.
- **허용 포맷**: 브랜드 가이드(md·PDF·이미지), 팔레트 표, 토큰 파일(json·css 변수), Figma 스타일 캡처 등. 포맷 불문 — §3의 요약 추출(4번)이 되면 톤 기준으로 쓴다.
- **awesome-design-md 9절 포맷**: VoltAgent의 awesome-design-md 카탈로그 파일은 frontmatter 토큰 대신 9개 절로 쓰인다. 아래처럼 매핑해 §3 요약 추출에 쓴다.

  | awesome-design-md 절 | 톤 기준 항목 |
  |---|---|
  | Visual Theme & Atmosphere | 톤 키워드 |
  | Color Palette & Roles | 팔레트 |
  | Typography Rules | 타이포 |
  | Component Stylings · Depth & Elevation · Layout Principles | 형태(radius·spacing·elevation) |
  | Do's and Don'ts | 금지(브리프 `피할 것`과 합친다) |
  | Responsive Behavior | 반응형 규칙 |
  | Agent Prompt Guide | 제작 프롬프트 참고(지시가 아니라 참고 — 우리 규격이 우선) |

- **타 사이트를 본뜬 DESIGN.md**(카탈로그의 실존 서비스 파일 등)는 기본 soft이며, [REFERENCE-DRIVEN.md](REFERENCE-DRIVEN.md)의 저작권 가드를 따른다 — 로고·고유 일러스트·상표성 있는 조합은 재현하지 않고 톤·체계만 참고한다.
- **톤 기준은 선택이다.** 없으면 파이프라인은 평소대로 진행한다(§5).

## 2. 구속 강도 (hard / soft)

| 강도 | 언제 | 하류 효과 |
|---|---|---|
| **hard(구속)** | 사용자 자신의 브랜드·제품의 확정 디자인 시스템 | 팔레트·타이포·톤·형태 = 하드 제약. 전략은 그 안에서만 콘셉트·구조를 탐색. 이탈은 근거 명시 + 전략 선택 게이트 승인 필요 |
| **soft(참고)** | 카탈로그에서 고른 출발점, 열망 레퍼런스, "이런 느낌" 예시 | 톤을 안내. 이탈 허용하되 근거를 기록 |

- 강도 기본 규칙: **자신의 브랜드 파일 = hard, 카탈로그·열망 예시 = soft.**
- 사용자가 명시된 강도·보존 조건을 주었으면 그대로 기록하고 재질문하지 않는다. 자신의 확정 브랜드 파일은 hard, 카탈로그·열망 예시는 soft로 분류해 근거를 알린다. 소유·적용 범위가 모호하거나 파일과 요청이 충돌해 실제 변경 허용치가 달라질 때만 구속/참고를 묻고 해당 의존 작업을 기다린다([HOST-COMPAT.md](HOST-COMPAT.md)).

## 3. 인테이크 (단계 0)

1. **범위 내 탐색(질문 금지 영역)**: 대상이 현재 참조하는 토큰·브랜드 가이드·DESIGN.md와 관련 context 기록부터 확인한다. 정본 경로·강도가 이미 확인됐고 변경되지 않았으면 재사용한다. 부족한 증거가 제약 결정을 막을 때만 탐색을 넓히고 무관한 outputs·브랜드 파일을 전수 탐색하지 않는다.
2. **필요한 자료 요청**: 브랜드 제약을 정하는 데 파일이 필요하고 자료에서 확인되지 않을 때 첨부를 요청한다. 사용자가 없다고 했거나 기존 자산 보존이 명확한 부분 수정에는 반복해서 묻지 않는다. 선택적 참고 자료는 필수 대기로 만들지 않는다.
3. **없다는 답이면**: 원하면 designmd.co나 awesome-design-md(VoltAgent)에서 출발점 DESIGN.md를 고를 수 있다고 안내한다. 없으면 승인된 목표 안에서 전략 단계에 새로 정한다. **자동으로 당겨오지 않는다. 특정 MCP를 요구하지 않는다.** 사용자가 카탈로그에서 골라 첨부하면 soft로 기록하며 명시된 강도는 존중한다. 모호한 경우만 §2에 따라 확인한다.
4. **요약 추출**: 첨부·발견된 파일을 정독해 아래를 뽑는다 —
   - 팔레트: primary·secondary·tertiary + semantic(success·warning·error) **hex**
   - 타이포: font family, 크기 스케일, weight, line-height
   - 형태: radius, spacing 스케일
   - 톤 키워드: Overview·personality 절 요약
   DESIGN.md면 frontmatter 토큰을 우선 읽고, 없으면 본문·산문에서 추출한다.
5. **브리프 기록**: 브리프의 `디자인 톤 기준` 항목에 **[강도] + 요약 + 원본 파일 경로**를 박는다. 원본 경로는 제작이 그대로 인용할 정본이다.

## 4. 단계별 흐름

- **전략**: hard의 팔레트·타이포·톤·형태는 제약이며, 방향 탐색이 필요하면 콘셉트·구조를 그 안에서 비교한다. hard 이탈 = 근거 + 승인, soft 이탈 = 근거 기록. 명시된 기존 강도·범위·승인은 재사용한다.
- **제작**: 기준에 맞는 hex·폰트·spacing·radius를 원본 경로와 함께 인용한다(즉흥 팔레트 금지). hard는 그대로 적용하고 승인된 이탈만 반영한다. soft 이탈은 근거와 적용 범위를 기록한다. 생성형(Gemini) 경로가 선택되면 적용 팔레트를 [PROMPT-PLAYBOOK.md](PROMPT-PLAYBOOK.md) §2.3 공통 스타일 블록에 주입한다.
- **검수**: 산출물이 톤 기준 토큰을 지켰는지 점검한다([REVIEW-AXES.md](REVIEW-AXES.md) 축 A 입력). hard = 근거 없는 이탈은 결함, soft = 이탈이 근거와 함께 기록됐는지 확인.

## 5. 톤 기준이 없을 때 (우아한 부재)

- 파이프라인은 평소대로 진행한다 — 팔레트·타이포는 전략 단계에서 근거와 함께 새로 정한다.
- 톤 기준 부재는 결함이 아니다. 검수의 톤 준수 점검은 "기준 없음 → 해당 없음"으로 건너뛴다.
