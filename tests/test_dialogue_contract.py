"""Normative instruction regressions, not proof of real-model dialogue behavior.

These checks protect consequential requirements and remove known competing
instructions. Live dialogue acceptance cases belong to the evaluation harness.
"""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def section(document, heading):
    return document.split(heading, 1)[1].split("\n## ", 1)[0]


class DialogueContractTests(unittest.TestCase):
    def test_decision_record_carries_identity_provenance_scope_and_dependencies(self):
        host = read("skills/gx-design/HOST-COMPAT.md")
        for field in ("id", "value", "status", "source", "scope-version", "dependencies"):
            self.assertIn(f"`{field}`", host)
        for state in ("미확정", "제안됨", "응답 대기", "사용자 확정", "위임됨", "변경됨"):
            self.assertIn(state, host)

    def test_unanswered_and_partial_required_decisions_keep_dependent_work_stopped(self):
        wait = section(read("skills/gx-design/HOST-COMPAT.md"), "## 답변 게이트")
        for case in ("질문 등록", "시간 경과", "창 닫기", "취소", "부분 답변", "자동 제출", "늦은 답"):
            self.assertIn(case, wait)
        self.assertRegex(wait, r"의존하는.*파일 변경.*위임.*중단")
        self.assertIn("결정 ID·범위 버전", wait)
        self.assertIn("나머지 필수 결정은 대기", wait)
        self.assertIn("현재 결정 버전", wait)

    def test_optional_preference_does_not_become_user_approval_or_delegation(self):
        host = read("skills/gx-design/HOST-COMPAT.md")
        self.assertIn("지정 없음", host)
        self.assertIn("응답 기회", host)
        self.assertIn("무응답을 사용자 승인·위임으로 기록하지 않는다", host)
        self.assertIn('"그만"·"멈춰"', host)
        self.assertIn("중단", host)

    def test_approval_reuse_is_scoped_and_invalidates_only_affected_dependencies(self):
        host = read("skills/gx-design/HOST-COMPAT.md")
        self.assertIn("## 승인 재사용과 변경", host)
        reuse = section(host, "## 승인 재사용과 변경")
        for obligation in ("요청에서 확정", "실물 제작 여부", "영향받는 승인과 산출물만", "게시", "브랜드"):
            self.assertIn(obligation, reuse)
        for path in ("skills/gx-design/SKILL.md", "skills/gx-redesign/SKILL.md"):
            doc = read(path)
            self.assertIn("승인 재사용", doc)
            self.assertNotIn("완료 기준: 실물 제작 여부를 물었고", doc)

    def test_modes_follow_request_without_a_forced_internal_mode_question(self):
        for path in ("skills/gx-design/SKILL.md", "skills/gx-redesign/SKILL.md"):
            modes = section(read(path), "## 모드 결정")
            with self.subTest(path=path):
                self.assertIn("요청 범위", modes)
                self.assertIn("실제 교환", modes)
                self.assertNotIn("첫 문항으로 모드를 묻는다", modes)
                self.assertNotIn("결합 모드 문항", modes)
        host = read("skills/gx-design/HOST-COMPAT.md")
        self.assertNotIn("모드+범위 결합", host)

    def test_question_quality_is_single_decision_with_grounded_recommendation_and_free_reply(self):
        host = read("skills/gx-design/HOST-COMPAT.md")
        for obligation in ("결정 하나", "근거가 없으면", "자유 응답", "복수 선택", "추천 거절", "모름"):
            self.assertIn(obligation, host)
        brief = read("skills/gx-design/BRIEF-INTERVIEW.md")
        self.assertNotIn("문항마다: 옵션 2~4개. 첫 옵션은 추천안", brief)
        self.assertNotIn("간단한 레이아웃 스케치를 붙이고", brief)

    def test_audit_finishes_without_an_exit_question_and_polish_has_no_silent_default(self):
        redesign = read("skills/gx-redesign/SKILL.md")
        self.assertIn("후속 행동을 짧게 안내", redesign)
        self.assertIn("필수 종료 질문", redesign)
        self.assertIn("D-01·D-03 수정, 나머지 유지", redesign)
        self.assertIn("ID 집합", redesign)
        self.assertNotIn("기본값은 Critical·Major 전부", redesign)
        self.assertNotIn("반드시 이어가기 게이트", redesign)
        self.assertNotIn("브리프 승인 → 진단 보고 저장 → 이어가기 선택", redesign)

    def test_targeted_refinement_reuses_direction_without_three_new_candidates(self):
        redesign = read("skills/gx-redesign/SKILL.md")
        self.assertIn("## 특정 지적·부분 다듬기", redesign)
        targeted = section(redesign, "## 특정 지적·부분 다듬기")
        for obligation in ("보존 조건", "관련 상태", "전략 3안", "재질문하지 않는다"):
            self.assertIn(obligation, targeted)
        twice = read("skills/gx-design/DESIGN-IT-TWICE.md")
        self.assertIn("방향이 열려", twice)
        self.assertIn("대표 영역·핵심 상태", twice)
        self.assertIn("전체 확장", twice)

    def test_intake_fact_finding_and_brand_strength_have_no_competing_gate(self):
        brief = read("skills/gx-design/BRIEF-INTERVIEW.md")
        design = read("skills/gx-design/SKILL.md")
        self.assertIn("중립적 사실 확인", brief)
        self.assertIn("중립적 사실 확인", design)
        self.assertNotIn("리서치도, 전략도, 디자인 산출물도 만들지 않는다", design)
        anchor = read("skills/gx-design/DESIGN-TONE-ANCHOR.md")
        self.assertNotIn("강도를 한 번 되물어 확정한다", anchor)
        self.assertIn("명시된 강도", anchor)
        self.assertIn("hard", anchor)
        self.assertIn("모호", anchor)


if __name__ == "__main__":
    unittest.main()
