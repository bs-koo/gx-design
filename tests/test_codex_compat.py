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


if __name__ == "__main__":
    unittest.main()
