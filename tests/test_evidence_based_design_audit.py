from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def assert_terms(
    testcase: unittest.TestCase,
    text: str,
    terms: tuple[str, ...],
) -> None:
    for term in terms:
        with testcase.subTest(term=term):
            testcase.assertIn(term, text)


class AntiTellChecklistContractTests(unittest.TestCase):
    def test_ui_web_gap_rules_are_present(self) -> None:
        text = read_doc("skills/gx-design/ANTI-TELL-CHECKLIST.md")
        assert_terms(
            self,
            text,
            (
                "장식용 이모지",
                "리퀴드 글라스",
                "근거 없는 리뷰",
                "벤토 그리드",
                "장식용 터미널",
                "3단계 요금제",
                "체크 표시 목록",
                "제품 화면·사용 과정·결과",
                "같은 큰 둥근 모서리",
                "이용약관",
                "개인정보처리방침",
            ),
        )

    def test_policy_links_require_real_routes_without_invented_facts(self) -> None:
        text = read_doc("skills/gx-design/ANTI-TELL-CHECKLIST.md")
        assert_terms(
            self,
            text,
            ("실제 경로", "임의로 만들지", "입력 필요"),
        )


class RedesignAuditContractTests(unittest.TestCase):
    def test_audit_reports_only_observed_findings(self) -> None:
        text = read_doc("skills/gx-redesign/SKILL.md")
        assert_terms(
            self,
            text,
            (
                "UI·웹 화면일 때만",
                "실제로 발견된 항목만",
                "해당 없음",
                "검증 한계",
                "왜 어색한지",
                "무엇으로 바꿀지",
            ),
        )

    def test_changes_are_locked_to_findings_or_approved_brief(self) -> None:
        text = read_doc("skills/gx-redesign/SKILL.md")
        assert_terms(
            self,
            text,
            (
                "변경 범위 잠금",
                "진단 문제 또는 승인된 개선 브리프 목표",
                "진단되지 않은 새 안티패턴",
            ),
        )


class RuntimeVerificationContractTests(unittest.TestCase):
    def test_visual_quality_covers_runtime_ui_checks(self) -> None:
        text = read_doc("skills/gx-design/VISUAL-QUALITY.md")
        assert_terms(
            self,
            text,
            (
                "데스크톱 대표 뷰포트",
                "모바일 대표 뷰포트",
                "주요 버튼",
                "내부·외부 링크",
                "키보드 Tab 이동 순서",
                "보이는 포커스",
                "WCAG AA 대비",
                "prefers-reduced-motion",
                "검증 불가: 비실행 산출물",
            ),
        )

    def test_review_axis_requires_runtime_log_for_executable_ui(self) -> None:
        text = read_doc("skills/gx-design/REVIEW-AXES.md")
        assert_terms(
            self,
            text,
            (
                "실행 검증 로그",
                "실행 가능한 UI",
                "Critical",
                "비실행 산출물",
            ),
        )


if __name__ == "__main__":
    unittest.main()
