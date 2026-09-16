import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAMES = {
    "gx-design", "gx-redesign", "design-research",
    "design-strategy", "creative-production", "creative-review",
}
CLAUDE_COMMANDS = "/plugin marketplace add bs-koo/gx-design\n/plugin install gx-design@gx-design"
CODEX_COMMANDS = "codex plugin marketplace add bs-koo/gx-design\ncodex plugin add gx-design@gx-design"


class InstallBlockParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks = []
        self.current = None
        self.code_host = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        if tag == "div" and "install" in classes:
            self.current = {"codes": {}, "buttons": []}
            self.blocks.append(self.current)
        if self.current is None:
            return
        if tag == "code" and "data-host" in attrs:
            self.code_host = attrs["data-host"]
            self.current["codes"][self.code_host] = ""
        if tag == "button" and "data-install-host" in attrs:
            self.current["buttons"].append(attrs)

    def handle_data(self, data):
        if self.current is not None and self.code_host:
            self.current["codes"][self.code_host] += data

    def handle_endtag(self, tag):
        if tag == "code":
            self.code_host = None


class CodexCompatibilityTests(unittest.TestCase):
    def test_local_skill_links_resolve(self):
        for path in (ROOT / "skills").rglob("*.md"):
            content = path.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)]+)\)", content):
                target = target.split("#", 1)[0]
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                with self.subTest(source=path.relative_to(ROOT), target=target):
                    self.assertTrue((path.parent / target).exists())

    def test_readme_explains_both_install_paths(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(CLAUDE_COMMANDS, text)
        self.assertIn(CODEX_COMMANDS, text)
        self.assertIn("docs/codex-skill-maintenance.md", text)
        self.assertTrue((ROOT / "docs/codex-skill-maintenance.md").exists())

    def test_site_has_two_accessible_host_install_blocks(self):
        text = (ROOT / "site/index.html").read_text(encoding="utf-8")
        parser = InstallBlockParser()
        parser.feed(text)
        self.assertEqual(len(parser.blocks), 2)
        for block in parser.blocks:
            with self.subTest(block=block):
                self.assertEqual(block["codes"].get("claude", "").strip(), CLAUDE_COMMANDS)
                self.assertEqual(block["codes"].get("codex", "").strip(), CODEX_COMMANDS)
                self.assertEqual({button.get("data-install-host") for button in block["buttons"]}, {"claude", "codex"})
                self.assertEqual([button.get("aria-pressed") for button in block["buttons"]], ["true", "false"])
        self.assertIn("docs/codex-skill-maintenance.md", text)
        self.assertIn("Claude Code와 Codex", text)
        self.assertIn("[data-install-host]", text)
        self.assertIn("[data-host]", text)

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

    def test_strategy_variants_have_main_agent_fallback(self):
        text = (ROOT / "skills/gx-design/DESIGN-IT-TWICE.md").read_text(encoding="utf-8")
        self.assertIn("HOST-COMPAT.md", text)
        self.assertIn("design-strategy", text)
        self.assertIn("위임할 수 없으면", text)
        self.assertIn("주 에이전트", text)
        self.assertIn("순서대로", text)
        self.assertNotIn("design-strategist 서브에이전트", text)
        for variant in ("A안", "B안", "C안"):
            self.assertIn(variant, text)

    def test_production_handoff_has_main_agent_gemini_fallback(self):
        text = (ROOT / "skills/gx-design/PRODUCTION-HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("HOST-COMPAT.md", text)
        self.assertIn("creative-production", text)
        self.assertIn("위임할 수 없으면", text)
        self.assertIn("주 에이전트", text)
        self.assertIn("PROMPT-PLAYBOOK.md", text)
        self.assertNotIn("creative-producer에게 위임한다", text)
        self.assertIn("outputs/final/YYYY-MM-DD_<project>_gemini-prompts.md", text)


if __name__ == "__main__":
    unittest.main()
