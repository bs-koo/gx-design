"""Instruction-loading regressions; no measured model-latency claim."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LoadingBudgetTests(unittest.TestCase):
    def test_narrow_review_does_not_reopen_all_ui_sections(self):
        text = (ROOT / "skills/gx-design/UI-QUALITY.md").read_text(encoding="utf-8")
        for label in ("gx-redesign 진단", "검수 축 B(완성도)·축 C(개선 목표 달성)"):
            row = next(line for line in text.splitlines() if line.startswith("| " + label + " |"))
            self.assertIn("§2", row)
            self.assertNotIn("전체", row)
            self.assertIn("범위", row)
        self.assertNotIn("축 B·축 C·진단은 이 문서 전체를 읽는다", text)

    def test_scoped_anti_tell_map_takes_precedence(self):
        text = (ROOT / "skills/gx-design/ANTI-TELL-CHECKLIST.md").read_text(encoding="utf-8")
        self.assertIn("모션만·오류 문구만", text)
        self.assertIn("범위가 한정된 행이 일반 UI 행보다 우선", text)
        self.assertIn("수정이 만든 회귀", text)


if __name__ == "__main__":
    unittest.main()
