import json
import hashlib
import re
import struct
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
# User-confirmed artifact identities: the legacy before/after filenames were inverted.
CASE_IMAGE_HASHES = {
    "before": "aa1ca8279c892d04ecea661a163c9c1cadb0cf00635b81048a278f2b60eb6c76",
    "after": "45a93724f0ce08f26412bcfb38e1c23c7d1ba2858f3f6e1ce9fa2bf1e260faed",
}
NAMED_CLAUDE_AGENTS = ("design-researcher", "design-strategist", "creative-producer")


def parse_frontmatter(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        closing = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return None

    fields = {}
    for line in lines[1:closing]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if separator and key.strip():
            fields[key.strip()] = value.strip().strip("\"'")
    return fields


def runtime_dependency_violations(text):
    violations = []
    forbidden_patterns = {
        "Claude-only model": r"(?im)^\s*model\s*:\s*(?:haiku|sonnet)\s*$",
        "automatic skills injection": r"(?im)^\s*skills\s*:",
        "named Claude agent": rf"(?i)\b(?:{'|'.join(NAMED_CLAUDE_AGENTS)})\b",
        "mandatory delegation": (
            r"(?i)(?:\b(?:must|always)\b.{0,120}\b(?:delegate|spawn|sub-?agents?)\b|"
            r"\b(?:delegate|spawn)\b.{0,120}\b(?:must|always)\b|"
            r"(?:반드시|무조건|항상).{0,120}(?:위임|서브에이전트|하위 작업자))"
        ),
    }
    for label, pattern in forbidden_patterns.items():
        if re.search(pattern, text):
            violations.append(label)

    fixed_delegation = re.compile(
        r"(?i)(?:(?:서브에이전트|하위 작업자|sub-?agents?).{0,120}"
        r"(?:위임한다|호출한다|생성한다|실행한다|\b(?:delegate|spawn)\b)|"
        r"에이전트(?:\s*\d+개)?(?:를|을)?\s*(?:병렬로\s*)?(?:호출|생성|스폰|실행)한다|"
        r"\bspawn\b.{0,40}\bagents?\b)"
    )
    for line in text.splitlines():
        if not fixed_delegation.search(line):
            continue
        has_capability_guard = any(
            phrase in line
            for phrase in ("도구가 있으면", "도구를 사용할 수 있으면", "위임이 허용되고", "위임할 수 있으면")
        )
        has_local_fallback = any(
            phrase in line
            for phrase in ("도구가 없으면", "위임할 수 없으면", "주 에이전트", "주 작업자")
        )
        if not (has_capability_guard and has_local_fallback):
            violations.append("fixed delegation")
            break
    return violations


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


class RedesignComparisonParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cards = []
        self.current = None
        self.reading_label = False
        self.label_tag = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        if "ba-label" in classes:
            self.current = {"label": "", "image": None}
            self.cards.append(self.current)
            self.reading_label = True
            self.label_tag = tag
        elif self.current is not None and tag == "img" and "ba-img" in classes:
            self.current["image"] = attrs

    def handle_data(self, data):
        if self.current is not None and self.reading_label:
            self.current["label"] += data

    def handle_endtag(self, tag):
        if tag == self.label_tag:
            self.reading_label = False
            self.label_tag = None
        elif tag == "figure":
            self.current = None


class CodexCompatibilityTests(unittest.TestCase):
    def test_skill_frontmatter_has_matching_identity_and_description(self):
        skill_paths = sorted((ROOT / "skills").glob("*/SKILL.md"))
        self.assertTrue(skill_paths, "at least one runtime skill must exist")
        for path in skill_paths:
            with self.subTest(path=path.relative_to(ROOT)):
                frontmatter = parse_frontmatter(path)
                self.assertIsNotNone(frontmatter, "SKILL.md must start with closed frontmatter")
                self.assertTrue(frontmatter.get("name", "").strip(), "frontmatter name must be nonempty")
                self.assertTrue(frontmatter.get("description", "").strip(), "frontmatter description must be nonempty")
                self.assertEqual(frontmatter["name"], path.parent.name)

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

    def test_readme_redesign_comparison_matches_before_after_columns(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        table = re.search(
            r"\| Before \| After \|\s*\n\|---\|---\|\s*\n"
            r"\| (?P<before>.*?) \| (?P<after>.*?) \|",
            text,
        )
        self.assertIsNotNone(table, "README must contain the Before/After comparison table")
        before = table.group("before")
        after = table.group("after")
        case = json.loads((ROOT / "site/assets/redesign-case.json").read_text(encoding="utf-8"))
        self.assertIn("개편 전", before)
        self.assertIn("site/assets/" + case["before"]["file"], before)
        self.assertIn("개편 후", after)
        self.assertIn("site/assets/" + case["after"]["file"], after)

    def test_public_maintenance_commands_do_not_use_machine_specific_paths(self):
        paths = (ROOT / "README.md", ROOT / "docs/codex-skill-maintenance.md")
        for path in paths:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertNotIn("C:/Users/SQI", text)
                self.assertNotIn("D:/SQ/design-plugin", text)
        maintenance = paths[1].read_text(encoding="utf-8")
        self.assertIn("$repo = (Get-Location).Path", maintenance)
        self.assertIn("$env:CODEX_HOME", maintenance)

    def test_site_has_host_install_commands_and_native_buttons(self):
        text = (ROOT / "site/index.html").read_text(encoding="utf-8")
        parser = InstallBlockParser()
        parser.feed(text)
        self.assertGreaterEqual(len(parser.blocks), 1)
        for block in parser.blocks:
            with self.subTest(block=block):
                self.assertEqual(block["codes"].get("claude", "").strip(), CLAUDE_COMMANDS)
                self.assertEqual(block["codes"].get("codex", "").strip(), CODEX_COMMANDS)
                self.assertEqual({button.get("data-install-host") for button in block["buttons"]}, {"claude", "codex"})
                self.assertTrue(all(button.get("type") == "button" for button in block["buttons"]))
        self.assertIn("docs/codex-skill-maintenance.md", text)
        self.assertIn("Claude Code와 Codex", text)

    def test_site_redesign_comparison_matches_labels_to_images(self):
        text = (ROOT / "site/index.html").read_text(encoding="utf-8")
        parser = RedesignComparisonParser()
        parser.feed(text)
        cards = {card["label"].strip(): card["image"] for card in parser.cards if card["image"] is not None}

        self.assertEqual(set(cards), {"BEFORE", "AFTER"})
        assets = ROOT / "site/assets"
        case = json.loads((assets / "redesign-case.json").read_text(encoding="utf-8"))
        for role, alt_marker in (("before", "개편 전"), ("after", "개편 후")):
            with self.subTest(role=role):
                entry = case[role]
                image = assets / entry["file"]
                self.assertEqual(image.parent.resolve(), assets.resolve())
                data = image.read_bytes()
                self.assertEqual(entry["sha256"], CASE_IMAGE_HASHES[role])
                self.assertEqual(hashlib.sha256(data).hexdigest(), CASE_IMAGE_HASHES[role])
                self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(struct.unpack(">II", data[16:24]), (entry["width"], entry["height"]))
                rendered = cards[role.upper()]
                self.assertEqual(rendered["src"], "assets/" + entry["file"])
                self.assertIn(alt_marker, rendered["alt"])
                self.assertEqual((int(rendered["width"]), int(rendered["height"])), (entry["width"], entry["height"]))
        self.assertFalse((assets / "redesign-before.png").exists())
        self.assertFalse((assets / "redesign-after.png").exists())

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
        self.assertRegex(review, r"축 A와 축 B를 순서대로(?: 각각)? 기록")
        self.assertIn("축 C", redesign)
        self.assertIn("위임할 수 없으면", redesign)

    def test_orchestrators_do_not_require_fixed_claude_agents(self):
        for path in sorted((ROOT / "skills").rglob("*.md")):
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(runtime_dependency_violations(text), [])

    def test_runtime_dependency_detector_rejects_equivalent_hard_dependencies(self):
        hard_dependencies = (
            "model: haiku",
            "skills:\n  - frontend-design",
            "design-strategist 에이전트에게 맡긴다.",
            "서브에이전트를 호출한다.",
            "에이전트 3개를 병렬로 생성한다.",
            "Always delegate this stage to sub-agents.",
        )
        for content in hard_dependencies:
            with self.subTest(content=content):
                self.assertTrue(runtime_dependency_violations(content))

    def test_question_headers_follow_the_active_host_capability(self):
        host = (ROOT / "skills/gx-design/HOST-COMPAT.md").read_text(encoding="utf-8")
        self.assertIn("구조", host)
        self.assertIn("도구", host)
        for relative_path in ("skills/gx-design/SKILL.md", "skills/gx-redesign/SKILL.md"):
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn("HOST-COMPAT.md", text)
            self.assertNotIn("첫 라운드의 첫 문항으로 모드를 묻는다", text)

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
        self.assertEqual(runtime_dependency_violations(text), [])
        self.assertIn("outputs/final/YYYY-MM-DD_<project>_gemini-prompts.md", text)


if __name__ == "__main__":
    unittest.main()
