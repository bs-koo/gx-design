# 디자인 톤 기준(Design Tone Anchor) 구현 계획

> 스펙: `docs/superpowers/specs/2026-07-24-design-tone-anchor-design.md`

**Goal:** 사용자 첨부 디자인 시스템 파일(DESIGN.md 등)을 톤 기준으로 받아 전략→제작→검수에 구속력 있게 물리는 경로 추가.

**Architecture:** 규칙을 신규 `DESIGN-TONE-ANCHOR.md` 하나에 중앙화하고, 브리프·SKILL·REVIEW-AXES·PROMPT-PLAYBOOK가 링크로 참조. 마크다운 스킬 편집이므로 인라인 실행 후 리뷰 서브에이전트 1개로 검수.

## Global Constraints

- designmd.co 자동 당김·MCP 의존 금지. 카탈로그는 "골라서 첨부할 출발점"으로 안내만.
- 톤 기준은 선택 — 부재 시 파이프라인은 평소대로 동작(우아한 부재).
- 게이트(브리프 승인·전략 선택·실물 제작) 불변. 톤 기준은 게이트를 추가하지 않는다.
- gx-redesign은 `../gx-design/DESIGN-TONE-ANCHOR.md` 교차 참조(기존 관례).

---

## Task 1: 신규 DESIGN-TONE-ANCHOR.md (중앙 규칙)

**Files:** Create `skills/gx-design/DESIGN-TONE-ANCHOR.md`

전문은 아래와 같이 작성한다(§1 정의 / §2 구속 강도 / §3 인테이크 / §4 단계별 흐름 / §5 우아한 부재).

## Task 2: BRIEF-INTERVIEW.md 인테이크 배선

**Files:** Modify `skills/gx-design/BRIEF-INTERVIEW.md`
- 사실 수집 목록에 톤 기준 파일 능동 탐색 줄 추가(→ DESIGN-TONE-ANCHOR).
- 결정 트리 중류에 "디자인 톤 기준 유무(없으면 이 라운드 첨부 요청)" 추가.
- 브리프 양식에 `디자인 톤 기준` 항목 추가.

## Task 3: REDESIGN-INTERVIEW.md 인테이크 배선

**Files:** Modify `skills/gx-redesign/REDESIGN-INTERVIEW.md`
- 자산 인벤토리 목록에 DESIGN.md/톤 기준 파일 추가(교차 참조).
- 자료 요청 목록에 톤 기준 파일 추가.
- 개선 브리프 양식에 `디자인 톤 기준` 항목 추가.

## Task 4: gx-design SKILL.md 단계 조항

**Files:** Modify `skills/gx-design/SKILL.md`
- 단계 2(Strategy): 톤 기준 있으면 팔레트·타이포·톤·형태는 제약. hard 이탈은 게이트 승인.
- 단계 3(Production): 위임에 원본 경로 전달, hex/폰트 그대로 인용, Gemini 병행 시 팔레트 주입.
- 단계 4(Review): 축 A에 톤 준수 점검 포함.

## Task 5: gx-redesign SKILL.md 단계 조항

**Files:** Modify `skills/gx-redesign/SKILL.md`
- 단계 3(개선 전략): 3안 모두 톤 기준 제약.
- 단계 4(제작): 위임에 원본 경로 + 인용.
- 단계 5(검수): 축 A에 톤 준수 점검.

## Task 6: REVIEW-AXES.md 축 A 준수 점검

**Files:** Modify `skills/gx-design/REVIEW-AXES.md`
- 축 A 입력/범위에 디자인 톤 기준 준수 추가(hard=이탈 결함, soft=근거 기록 확인).

## Task 7: PROMPT-PLAYBOOK.md 팔레트 주입

**Files:** Modify `skills/gx-design/PROMPT-PLAYBOOK.md`
- §2.3 공통 스타일 블록에 "톤 기준 있으면 그 팔레트/폰트/톤을 정본 소스로" 조항.

## Task 8: 버전·소개 갱신

**Files:** Modify `README.md`, `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json`
- 톤 기준 소개 1줄, 버전 0.4.0 → 0.5.0.

## Task 9: 최종 검수

리뷰 서브에이전트 1개로 교차 참조 일관성·규칙 중복·게이트 불변 검수. Critical 있으면 수정 후 재검수.
