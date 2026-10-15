import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class CoreModeInterviewTests(unittest.TestCase):
    def test_host_compat_has_no_core_round_cap(self) -> None:
        host = read_doc("skills/gx-design/HOST-COMPAT.md")
        self.assertNotIn("1라운드 4슬롯", host)
        self.assertNotIn("2라운드를 열지 않는다", host)
        self.assertIn("frontier가 빌 때까지", host)
        self.assertIn("그만, 진행해", host)

    def test_brief_interview_core_clause_matches_full(self) -> None:
        brief = read_doc("skills/gx-design/BRIEF-INTERVIEW.md")
        clause = brief.split("## 핵심 모드 조항", 1)[1].split("\n## ", 1)[0]
        self.assertIn("인터뷰 절차는 모드와 무관하게 동일하다", clause)
        self.assertNotIn("라운드를 1회로 제한", clause)
        self.assertNotIn("핵심 여정은 묻지 않고", brief)

    def test_skills_do_not_cap_core_interview(self) -> None:
        for relative_path in (
            "skills/gx-design/SKILL.md",
            "skills/gx-redesign/SKILL.md",
            "skills/gx-redesign/REDESIGN-INTERVIEW.md",
        ):
            text = read_doc(relative_path)
            with self.subTest(path=relative_path):
                self.assertNotIn("1라운드로 제한", text)
                self.assertNotIn("라운드는 1회로 제한", text)
                self.assertIn("frontier가 빌 때까지", text)
        for relative_path in ("skills/gx-design/SKILL.md", "skills/gx-redesign/SKILL.md"):
            with self.subTest(path=relative_path):
                self.assertIn("핵심 모드라서 질문을 줄이고 [가정]으로 채웠다", read_doc(relative_path))

    def test_readme_does_not_promise_single_round(self) -> None:
        readme = read_doc("README.md")
        self.assertNotIn("인터뷰 1라운드", readme)
        self.assertNotIn("(전체 모드 기준)", readme)


if __name__ == "__main__":
    unittest.main()
