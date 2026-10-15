import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET_VERSION = "0.11.0"
NAMED_CLAUDE_AGENTS = ("design-researcher", "design-strategist", "creative-producer")


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


# 스펙 §4 필수 앵커 문자열 (docs/superpowers/specs/2026-10-15-motion-guide-audit-mode-design.md)
ANCHORS = {
    "skills/gx-design/MOTION.md": (
        "## A. UI 인터랙션",
        "## B. 모션 그래픽·영상",
        "## C. 모션 점검 출력",
        "cubic-bezier(0.23, 1, 0.32, 1)",
        "scale(0.97)",
        "(hover: hover) and (pointer: fine)",
        "ease-in",
        "프레임",
        "안전영역",
        "Before | After | Why",
    ),
    "skills/gx-design/VISUAL-CRAFT.md": ("MOTION.md", "1–3", "8–10", "프리미엄 프리셋"),
    "skills/gx-design/VISUAL-QUALITY.md": ("polish", "핵심 여정", "컨택트 시트", "@playwright/mcp@latest"),
    "skills/gx-design/BRIEF-INTERVIEW.md": ("요청 해석 카드", "피할 것", "핵심 여정"),
    "skills/gx-design/DESIGN-IT-TWICE.md": ("다이얼", "모션 범위"),
    "skills/gx-redesign/SKILL.md": ("점검 전용", "이어가기 게이트", "MOTION.md"),
    "skills/gx-design/DESIGN-TONE-ANCHOR.md": ("awesome-design-md",),
    "skills/creative-production/SKILL.md": ("MOTION.md", "fps"),
    "skills/creative-review/SKILL.md": ("MOTION.md",),
    "README.md": ("## 이렇게 시키세요", "MOTION.md", "점검 전용"),
}

MOTION_CONSUMERS = (
    "skills/gx-design/VISUAL-CRAFT.md",
    "skills/gx-design/VISUAL-QUALITY.md",
    "skills/creative-production/SKILL.md",
    "skills/creative-review/SKILL.md",
    "skills/gx-redesign/SKILL.md",
)


class MotionGuideAnchorTests(unittest.TestCase):
    def test_spec_anchor_strings_are_present(self) -> None:
        for relative_path, terms in ANCHORS.items():
            with self.subTest(path=relative_path):
                self.assertTrue((ROOT / relative_path).exists(), f"{relative_path} must exist")
                assert_terms(self, read_doc(relative_path), terms)


class MotionDeliveryTests(unittest.TestCase):
    def test_motion_guide_is_linked_from_consumers(self) -> None:
        link = re.compile(r"\]\((?:\.\./gx-design/|\./)?MOTION\.md(?:#[^)]*)?\)")
        for relative_path in MOTION_CONSUMERS:
            with self.subTest(path=relative_path):
                self.assertRegex(read_doc(relative_path), link)

    def test_motion_guide_separates_ui_and_video_rules(self) -> None:
        text = read_doc("skills/gx-design/MOTION.md")
        ui = text.index("## A. UI 인터랙션")
        video = text.index("## B. 모션 그래픽·영상")
        review = text.index("## C. 모션 점검 출력")
        self.assertLess(ui, video)
        self.assertLess(video, review)


class ActiveSkillHostCompatTests(unittest.TestCase):
    FORBIDDEN = ("AskUserQuestion", "multiSelect", "preview를 쓴다", "WebSearch")

    def test_forbidden_host_specific_strings_are_absent(self) -> None:
        for path in sorted((ROOT / "skills").rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            for term in self.FORBIDDEN:
                with self.subTest(path=path.relative_to(ROOT), term=term):
                    self.assertNotIn(term, text)

    def test_no_named_agents_or_fixed_models_in_skills(self) -> None:
        agent_pattern = re.compile(rf"(?i)\b(?:{'|'.join(NAMED_CLAUDE_AGENTS)})\b")
        model_pattern = re.compile(r"(?im)^\s*model\s*:\s*(?:haiku|sonnet|opus)\s*$")
        for path in sorted((ROOT / "skills").rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIsNone(agent_pattern.search(text))
                self.assertIsNone(model_pattern.search(text))


class UserGuideSurfaceTests(unittest.TestCase):
    def test_readme_examples_show_both_hosts(self) -> None:
        text = read_doc("README.md")
        section = text.split("## 이렇게 시키세요", 1)[1].split("\n## ", 1)[0]
        assert_terms(
            self,
            section,
            (
                "[뻔한 X 말고 Y처럼]",
                "/gx-design:gx-design",
                "/gx-design:gx-redesign",
                "$gx-design",
                "$gx-redesign",
                "### 디자인 스킬 5개를 따로 설치하지 않아도",
                "MIT",
                "Apache-2.0",
            ),
        )

    def test_site_has_ask_section_with_host_toggle(self) -> None:
        text = read_doc("site/index.html")
        assert_terms(
            self,
            text,
            ("이렇게 시키세요", "data-ask-choice", "data-ask-host", "/gx-design:gx-redesign", "$gx-redesign"),
        )


class VersionTests(unittest.TestCase):
    def test_plugin_versions_are_target(self) -> None:
        claude = json.loads(read_doc(".claude-plugin/plugin.json"))
        codex = json.loads(read_doc(".codex-plugin/plugin.json"))
        self.assertEqual(claude["version"], TARGET_VERSION)
        self.assertEqual(codex["version"].split("+", 1)[0], TARGET_VERSION)
        marketplace = json.loads(read_doc(".claude-plugin/marketplace.json"))
        for plugin in marketplace.get("plugins", []):
            if "version" in plugin:
                with self.subTest(plugin=plugin.get("name")):
                    self.assertEqual(plugin["version"], TARGET_VERSION)


if __name__ == "__main__":
    unittest.main()
