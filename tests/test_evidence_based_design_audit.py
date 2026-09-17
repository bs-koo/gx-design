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


if __name__ == "__main__":
    unittest.main()

class RedesignAuditContractTests(unittest.TestCase):
    def test_audit_reports_only_observed_findings(self) -> None:
        text = read_doc("skills/gx-redesign/SKILL.md")
        assert_terms(self, text, ("UI and web screens", "observed findings", "N/A", "before", "after", "ANTI-TELL-CHECKLIST.md"))

    def test_changes_are_locked_to_findings_or_approved_brief(self) -> None:
        text = read_doc("skills/gx-redesign/SKILL.md")
        assert_terms(self, text, ("Change scope lock", "diagnosed problem or an approved brief improvement goal", "Axis C"))
