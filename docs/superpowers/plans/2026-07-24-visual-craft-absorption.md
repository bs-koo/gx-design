# 시각 크래프트 규칙 흡수 구현 계획

> 스펙: `docs/superpowers/specs/2026-07-24-visual-craft-absorption-design.md`

**Goal:** frontend-design·taste·animate의 구체 규칙을 우리 VISUAL-CRAFT.md로 흡수하고 제작·검수·품질 루프가 참조하게 한다. 외부 스킬 의존 0.

## Global Constraints

- 커뮤니티 스킬(taste·animate) 런타임 의존 금지 — 규칙만 우리 문장으로 흡수.
- 디자인 톤 기준이 상위 — 다이얼·일관성은 톤 기준 안에서.
- taste 다이얼은 승인된 전략에 종속(전략 대체 금지).
- 적용 범위 = UI·그래픽·코드 렌더 레그(Gemini 프롬프트 레그 제외).
- 게이트 불변.

## Task 1: 신규 VISUAL-CRAFT.md

`skills/gx-design/VISUAL-CRAFT.md` — §1 안티-슬롭 / §2 톤 다이얼(VARIANCE·MOTION·DENSITY) / §3 일관성 잠금 / §4 모션(60fps·transform·opacity) / §5 시그니처·절제 / §6 카피. 톤 기준 상위·전략 종속 명시.

## Task 2: VISUAL-QUALITY.md

- 절차 3 비평에 VISUAL-CRAFT를 렌즈로 추가.
- 절차 2 캡처에 Playwright MCP 가용 시 뷰포트별 캡처·비교, 없으면 PNG Read 폴백.

## Task 3: creative-production/SKILL.md

제작 원칙에 "gx-design의 VISUAL-CRAFT 규격 준수(UI·그래픽 산출물은 3 다이얼 기록·일관성 잠금)" 추가.

## Task 4: creative-review/SKILL.md

시각 완성도/렌더 실물 절에 안티-슬롭·일관성 잠금·모션 QA 항목 추가(VISUAL-CRAFT 기준).

## Task 5: creative-producer.md

작업 원칙에 VISUAL-CRAFT 준수 1줄.

## Task 6: 버전·소개

plugin.json 0.5.0→0.6.0, marketplace.json·README 반영.

## Task 7: 리뷰 서브에이전트 검수 → PR.
