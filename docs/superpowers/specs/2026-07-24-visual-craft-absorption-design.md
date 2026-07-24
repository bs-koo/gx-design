# 시각 크래프트 규칙 흡수(Visual Craft Absorption) 설계

- **일자**: 2026-07-24
- **대상**: gx-design 제작·검수·시각 품질 레이어
- **상태**: 승인됨(B안 채택) — 브랜치 `feat/visual-craft`
- **버전 영향**: 0.5.0 → 0.6.0 (사용자향 품질 능력 추가 = minor)

## 목표(한 문장)

frontend-design(공식)·taste-skill·animate(커뮤니티) 스킬의 **구체 크래프트 규칙을 우리 규격으로 흡수**해, 코드 렌더·UI·그래픽 산출물의 "조잡함"을 제작·검수 단계에서 잡는다. 외부 스킬 의존 없음.

## 배경 / 결정

- 조사 결과: frontend-design(공식, 이미 연동)·playwright-mcp(MCP, 이미 연동)는 활용 심화, taste·animate는 커뮤니티 서드파티.
- **A안(외부 스킬 옵션 의존) 대신 B안(규칙 흡수) 채택** — 이유: (1) 커뮤니티 스킬 하드 의존 회피, (2) frontend-design과 taste가 같은 영역(타이포·팔레트)을 강제해 충돌 위험, (3) PROMPT-PLAYBOOK이 Google 가이드를 흡수한 것과 동일한 검증된 패턴.
- 적용 범위는 **UI·그래픽·코드 렌더 레그**로 한정 — 이 규칙들은 CSS/모션 크래프트라 Gemini 이미지/영상 프롬프트 레그에는 직접 적용되지 않는다(과대적용 금지).

## 흡수할 규칙 (출처 → 우리 규격)

- **frontend-design**: 안티-슬롭 3대 기본 룩 회피 / hero=논지 / 타이포가 인격 / 구조=정보(넘버링은 실제 시퀀스일 때만) / 시그니처 하나에 대담함 집중 / 품질 바닥(반응형·키보드 포커스·reduced-motion) / 카피도 디자인 재료.
- **taste-skill**: 3 다이얼 — VARIANCE(비대칭)/MOTION(모션 강도)/DENSITY(밀도)를 브리프 vibe·타깃에서 도출. 일관성 잠금 — accent 1개·radius 체계 1개·라이트/다크 1회 확정.
- **animate**: transform·opacity만 60fps / 나가는 모션 < 들어오는 모션 / 모션은 주제를 섬길 때만, 과하면 AI 인상.

## 아키텍처 — 중앙화

**신규 `skills/gx-design/VISUAL-CRAFT.md`** 하나에 흡수 규칙을 모으고(§1 안티-슬롭 / §2 톤 다이얼 / §3 일관성 잠금 / §4 모션 / §5 시그니처·절제 / §6 카피), 나머지는 참조한다.

- `VISUAL-QUALITY.md`(같은 디렉터리): `VISUAL-CRAFT.md` 링크 참조를 비평 렌즈로 추가.
- `creative-production`·`creative-review`(별도 스킬 디렉터리): 기존 관례대로 "gx-design 스킬의 VISUAL-CRAFT 규격"으로 **이름 참조**(PROMPT-PLAYBOOK를 이름 참조하는 것과 동일).
- `agents/creative-producer.md`: VISUAL-CRAFT 준수 1줄 추가.

## Playwright 루프 승격 (이미 있는 MCP 활용 심화)

`VISUAL-QUALITY.md` 절차에 — 비평용 이미지 확보 시 **Playwright MCP가 가용하면 뷰포트별 캡처 + 레퍼런스 비교**로 잡고, 없으면 기존처럼 렌더 PNG를 Read로 직접 연다(폴백). 새 하드 의존을 만들지 않는다.

## 톤 기준과의 관계

디자인 톤 기준([[DESIGN-TONE-ANCHOR]])이 있으면 **톤 기준이 상위**다 — 3 다이얼·일관성은 톤 기준 팔레트·타이포 안에서 정한다. VISUAL-CRAFT는 톤 기준을 대체하지 않는다.

## 전략 게이트 보호

taste의 다이얼은 "vibe에서 자동으로 디자인을 밀어붙이는" 성격이 있으므로, **승인된 전략에 종속된 제작 실행 보조**로만 쓴다. 전략 대체재로 쓰지 않는다(designmd.co·톤 기준과 동일 원칙).

## 변경 파일

1. 신규 `skills/gx-design/VISUAL-CRAFT.md`
2. `skills/gx-design/VISUAL-QUALITY.md` — 비평 렌즈 + Playwright 캡처 승격
3. `skills/creative-production/SKILL.md` — 제작 원칙에 VISUAL-CRAFT(다이얼 기록·크래프트 규칙)
4. `skills/creative-review/SKILL.md` — 시각 완성도/렌더 절에 안티-슬롭·일관성·모션 QA
5. `agents/creative-producer.md` — VISUAL-CRAFT 준수 원칙
6. `README.md` — 참조 목록 + 버전
7. `.claude-plugin/plugin.json` — 0.5.0 → 0.6.0
8. `.claude-plugin/marketplace.json` — 소개 반영

## 비목표(YAGNI)

- taste·animate 스킬을 런타임 의존으로 연결하지 않는다(설치 요구 없음).
- 전략(DESIGN-IT-TWICE)·Gemini 프롬프트 규격(PROMPT-PLAYBOOK)은 이번에 건드리지 않는다(범위 밖).
- 프로그램식 CSS 린터/모션 검증기 도입 없음.

## 실행 방식

변경 8건이 VISUAL-CRAFT.md 계약을 공유하고 교차 참조가 상호 의존하므로 인라인 구현 후 리뷰 서브에이전트 1개로 검수(톤 기준 작업과 동일 판단).
