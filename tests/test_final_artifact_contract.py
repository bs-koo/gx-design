"""Instruction contracts only; these checks do not measure real-model quality."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def doc(name):
    return (ROOT / name).read_text(encoding="utf-8")


class FinalArtifactContractTests(unittest.TestCase):
    def test_review_binds_verdict_to_artifact_and_observed_conditions(self):
        text = doc("skills/gx-design/REVIEW-AXES.md")
        for field in ("산출물 경로", "버전 또는 해시", "fixture", "상태", "뷰포트", "실행 환경", "범위 버전"):
            with self.subTest(field=field):
                self.assertIn(field, text)
        self.assertIn("같은 빌드의 다른 상태", text)
        self.assertRegex(text, r"수정·재생성·내보내기[\s\S]*영향받는")

    def test_required_major_and_missing_evidence_block_pass_without_global_zero(self):
        text = doc("skills/gx-design/REVIEW-AXES.md")
        self.assertIn("범위 내 필수 Critical·Major", text)
        self.assertIn("필수 수용 조건이 미검증이면", text)
        self.assertIn("범위 밖 미검증", text)
        self.assertIn("전역 Major 0건", text)
        self.assertNotIn("두 축 모두 Critical 0건이면", text)
        self.assertNotIn("Major 이하는 기록만", text)

    def test_accepted_exception_is_not_a_fixed_pass(self):
        for path in ("skills/gx-design/REVIEW-AXES.md", "skills/creative-review/SKILL.md"):
            with self.subTest(path=path):
                text = doc(path)
                self.assertIn("예외 수용", text)
                self.assertIn("해결된 통과", text)
                self.assertIn("수정 필요", text)
                self.assertIn("미검증", text)

    def test_revalidation_follows_impact_across_axes_and_journeys(self):
        text = doc("skills/gx-design/REVIEW-AXES.md")
        for field in ("영향 기반 재검수", "A/C", "브랜드", "모바일", "여정", "회귀"):
            self.assertIn(field, text)
        self.assertNotIn("그 축만", text)
        self.assertNotIn("해당 축만 재점검", text)

    def test_one_total_budget_covers_producer_and_review_corrections(self):
        text = doc("skills/gx-design/RUN-BUDGET.md")
        for field in ("기본 총 3회", "제작자 polish", "검수 후 수정", "관찰 → 묶음 수정 → 재검증", "도구 호출", "범위 버전"):
            self.assertIn(field, text)
        self.assertIn("자동 초기화하지", text)
        self.assertIn("범위를 조용히 확대하지", text)

    def test_observation_does_not_force_mutation_or_an_extra_loop(self):
        text = doc("skills/gx-design/VISUAL-QUALITY.md")
        self.assertIn("관찰·판정은 최소 1회", text)
        self.assertIn("결함이 없으면 수정하지", text)
        self.assertIn("RUN-BUDGET.md", text)
        self.assertNotIn("루프는 **최소 1회, 최대 3회**", text)
        self.assertNotIn("자체 비평 Critical 0건이면", text)

    def test_handoff_reuses_approved_route_and_preserves_non_ui_outputs(self):
        text = doc("skills/gx-design/PRODUCTION-HANDOFF.md")
        self.assertIn("이미 확정·위임된 경로", text)
        self.assertIn("다시 묻지", text)
        self.assertIn("미확정 필수 결정", text)
        for route in ("Gemini", ".pen", "MP4", "BX", "문서로 종료"):
            self.assertIn(route, text)
        self.assertNotIn("실물 제작 여부를 물었다(", text)
        self.assertNotIn("순수 문서만 남는 경우가 아니면 게이트를 생략하지", text)

    def test_each_region_has_purpose_behavior_and_format(self):
        for path in ("skills/gx-design/PRODUCTION-HANDOFF.md", "skills/creative-production/SKILL.md"):
            with self.subTest(path=path):
                text = doc(path)
                for field in ("영역별", "사용 목적", "실제 동작", "연출", "형식", "CTA", "폼"):
                    self.assertIn(field, text)

    def test_b_review_observes_before_raw_logs_and_has_runnable_handoff(self):
        text = doc("skills/gx-design/REVIEW-AXES.md")
        self.assertRegex(text, r"먼저 실물[\s\S]*그다음 원시 실행 로그")
        for field in ("URL/파일", "실행 방법", "인증 상태", "시작 화면", "fixture 초기화", "도구 능력", "자기평가"):
            self.assertIn(field, text)
        self.assertNotIn("VISUAL-QUALITY.md의 렌더 품질 로그 포함", text)

    def test_producer_returns_version_evidence_and_respects_prompt_only_scope(self):
        for path in ("skills/creative-production/SKILL.md", "agents/creative-producer.md"):
            with self.subTest(path=path):
                text = doc(path)
                for field in ("버전 또는 해시", "변경 ID", "미검증", "프롬프트만", "생성을 추가하지"):
                    self.assertIn(field, text)

    def test_static_actual_size_check_is_reachable_without_video_section(self):
        text = doc("skills/gx-design/VISUAL-QUALITY.md")
        common = text.split("## 영상 분기", 1)[0]
        self.assertIn("BX·그래픽은 실제 사용 크기", common)

    def test_simple_work_has_concrete_lightweight_execution_defaults(self):
        text = doc("skills/gx-design/RUN-BUDGET.md")
        for term in ("단순 audit·polish", "오케스트레이터 1개", "자동 리서치·전략·서브에이전트 분기", "대표 상태 1개", "추가 위험", "상한이며 필수 작업량이 아니다", "간결한 이슈·변경·증거 로그"):
            self.assertIn(term, text)
        self.assertNotIn("리서치를 경량 실행(통합 리포트 1개)", text)

    def test_core_strategy_allows_one_recommendation_and_only_needed_comparison(self):
        text = doc("skills/gx-design/RUN-BUDGET.md")
        for term in ("핵심 모드", "추천 1안", "비교 1안", "명시적 3안", "전체 모드"):
            self.assertIn(term, text)
        self.assertNotIn("한 주체가 스케치 3안을 쓴다", text)

    def test_capture_budget_is_risk_based_and_rules_are_cached(self):
        visual = doc("skills/gx-design/VISUAL-QUALITY.md")
        self.assertIn("대표 상태 1개", visual)
        self.assertIn("일괄", visual)
        self.assertNotIn("대표 화면) 2~3장을 먼저 렌더", visual)
        self.assertNotIn("검수 축 B는 이 문서 전체를 읽는다", visual)
        budget = doc("skills/gx-design/RUN-BUDGET.md")
        self.assertIn("세션당 한 번", budget)
        self.assertIn("변경되지 않은 규칙", budget)
        self.assertIn("현재 매체·축", budget)

    def test_lightweight_review_has_no_automatic_parallel_fanout(self):
        review = doc("skills/gx-design/REVIEW-AXES.md")
        self.assertIn("단순 audit·polish", review)
        self.assertIn("최종 축 B", review)
        self.assertIn("작업 위험·규모", review)
        self.assertNotIn("핵심 모드에서도 검수 독립성은 줄이지 않는다", review)

    def test_product_severity_and_procedural_evidence_gap_are_separate(self):
        text = doc("skills/gx-design/REVIEW-AXES.md")
        self.assertIn("제품 결함 심각도", text)
        self.assertIn("절차·증거 누락", text)
        self.assertIn("필수 수용 조건이 미검증이면", text)

    def test_narrow_motion_review_does_not_reopen_unrelated_visual_rules(self):
        review = doc("skills/gx-design/REVIEW-AXES.md")
        b_input = next(line for line in review.splitlines() if "첫 관찰 입력 =" in line)
        self.assertIn("시각 구조·AI 티가 검수 범위", b_input)
        self.assertIn("모션이 검수 범위", b_input)
        self.assertIn("모션만 점검", review)
        self.assertIn("§2 증거 계약", review)
        visual = doc("skills/gx-design/VISUAL-QUALITY.md")
        b_map = next(line for line in visual.splitlines() if line.startswith("| 검수 축 B |"))
        self.assertIn("현재 요청·범위", b_map)
        self.assertNotIn("| 전체 |", b_map)
        self.assertIn("모션만 점검", visual)
        self.assertNotIn("비평 기준은 절차 3의 항목 전부다", visual)


if __name__ == "__main__":
    unittest.main()
