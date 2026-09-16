import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAMES = {
    "gx-design", "gx-redesign", "design-research",
    "design-strategy", "creative-production", "creative-review",
}


class CodexCompatibilityTests(unittest.TestCase):
    def test_codex_manifest_matches_claude_identity(self):
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        codex_manifest = ROOT / ".codex-plugin/plugin.json"
        self.assertTrue(codex_manifest.exists(), "Codex manifest must exist")
        codex = json.loads(codex_manifest.read_text(encoding="utf-8"))
        self.assertEqual(codex["name"], claude["name"])
        self.assertEqual(codex["version"].split("+", 1)[0], claude["version"])
        self.assertEqual(codex["author"]["name"], claude["author"]["name"])
        self.assertEqual(codex["skills"], "./skills/")
        self.assertTrue(codex["description"].strip())
        self.assertEqual(set(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")), SKILL_NAMES)

    def test_active_skills_do_not_require_claude_question_tool(self):
        for path in (ROOT / "skills").rglob("*.md"):
            with self.subTest(path=path.relative_to(ROOT)):
                content = path.read_text(encoding="utf-8")
                self.assertNotIn("AskUserQuestion", content)
                self.assertNotIn("multiSelect", content)
                self.assertNotIn("preview를 쓴다", content)
                self.assertNotIn("WebSearch", content)
                self.assertNotIn("WebFetch", content)
                self.assertNotIn("Read로", content)

    def test_host_contract_is_present(self):
        host = (ROOT / "skills/gx-design/HOST-COMPAT.md").read_text(encoding="utf-8")
        for section in ("질문·선택", "답변 게이트", "위임", "도구 가용성"):
            self.assertIn(section, host)

    def test_orchestrators_link_host_contract_and_specialist_skills(self):
        for name in ("gx-design", "gx-redesign"):
            with self.subTest(name=name):
                text = (ROOT / f"skills/{name}/SKILL.md").read_text(encoding="utf-8")
                self.assertIn("HOST-COMPAT.md", text)
                for specialist in ("design-research", "design-strategy", "creative-production"):
                    self.assertIn(specialist, text)
                self.assertIn("위임할 수 없", text)

    def test_specialist_skills_define_role_contract(self):
        for name in ("design-research", "design-strategy", "creative-production"):
            with self.subTest(name=name):
                text = (ROOT / f"skills/{name}/SKILL.md").read_text(encoding="utf-8")
                self.assertIn("## 역할과 산출물 계약", text)
                self.assertIn("입력은", text)
                self.assertIn("출력은", text)
                self.assertIn(f"outputs/{'production' if name == 'creative-production' else name.split('-', 1)[1]}/", text)

    def test_review_axes_and_redesign_support_sequential_fallback(self):
        review = (ROOT / "skills/gx-design/REVIEW-AXES.md").read_text(encoding="utf-8")
        redesign = (ROOT / "skills/gx-redesign/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("위임할 수 없으면", review)
        self.assertIn("축 A와 축 B를 순서대로 각각 기록", review)
        self.assertIn("축 C", redesign)
        self.assertIn("위임할 수 없으면", redesign)

    def test_orchestrators_do_not_require_fixed_claude_agents(self):
        paths = (
            ROOT / "skills/gx-design/SKILL.md",
            ROOT / "skills/gx-redesign/SKILL.md",
            ROOT / "skills/gx-design/REVIEW-AXES.md",
        )
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                for agent in ("design-researcher", "design-strategist", "creative-producer"):
                    self.assertNotIn(agent, text)
                self.assertNotIn("병렬 스폰한다", text)


if __name__ == "__main__":
    unittest.main()
