"""Reviewed timing annotations measure turn boundaries, not model quality."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("eval_benchmark", ROOT / "evals" / "benchmark.py")
benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)


def result():
    return {"scenario": "T17", "mode": "core", "stop_reason": "completed",
            "elapsed_seconds": 15.5,
            "turns": [{"turn": 1, "elapsed_seconds": 2.0},
                      {"turn": 2, "elapsed_seconds": 5.0},
                      {"turn": 3, "elapsed_seconds": 7.0}]}


def review(**updates):
    value = {"reviewer": "local reviewer", "evidence": "Turn 2 contains the scoped usable result.",
             "first_useful_turn": 2, "rework_turns": [3]}
    value.update(updates)
    return value


class ReviewedTimingTests(unittest.TestCase):
    def test_first_useful_time_sums_through_reviewed_turn_and_keeps_total(self):
        report = benchmark.summarize(result(), review())
        self.assertEqual(report["first_useful_cli_seconds_upper_bound"], 7.0)
        self.assertEqual(report["total_cli_seconds"], 14.0)
        self.assertEqual(report["total_elapsed_seconds"], 15.5)
        self.assertEqual(report["rework_turn_count"], 1)
        self.assertEqual(report["rework_cli_seconds"], 7.0)
        self.assertEqual(report["reviewer"], "local reviewer")
        self.assertEqual(report["timing_basis"], "reviewed_turn_boundaries")

    def test_unobserved_useful_result_stays_unknown_even_if_completed(self):
        report = benchmark.summarize(result(), review(first_useful_turn=None, rework_turns=[]))
        self.assertIsNone(report["first_useful_cli_seconds_upper_bound"])
        self.assertEqual(report["rework_turn_count"], 0)

    def test_missing_timing_is_not_counted_as_zero(self):
        data = result()
        del data["turns"][0]["elapsed_seconds"]
        report = benchmark.summarize(data, review())
        self.assertIsNone(report["first_useful_cli_seconds_upper_bound"])
        self.assertIsNone(report["total_cli_seconds"])
        self.assertFalse(report["timing_complete"])
        self.assertEqual(report["rework_cli_seconds"], 7.0)

    def test_invalid_or_unrecorded_turns_are_rejected(self):
        for value in (0, -1, 4, True, 1.5, "2"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                benchmark.summarize(result(), review(first_useful_turn=value))
        for turns in ([3, 3], [0], [4], [True], "3"):
            with self.subTest(turns=turns), self.assertRaises(ValueError):
                benchmark.summarize(result(), review(rework_turns=turns))

    def test_judgment_requires_named_reviewer_and_evidence(self):
        for field in ("reviewer", "evidence"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                benchmark.summarize(result(), review(**{field: " "}))

    def test_nonfinite_negative_and_boolean_time_is_rejected(self):
        for value in (-1, True, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                data = result()
                data["turns"][0]["elapsed_seconds"] = value
                benchmark.summarize(data, review())

    def test_stopped_run_is_reported_without_claiming_completion(self):
        data = result()
        data["stop_reason"] = "waiting"
        report = benchmark.summarize(data, review(first_useful_turn=None))
        self.assertEqual(report["stop_reason"], "waiting")
        self.assertIsNone(report["first_useful_cli_seconds_upper_bound"])

    def test_command_reads_review_and_does_not_modify_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "T17-core.json"
            path.write_text(json.dumps(result()), encoding="utf-8")
            path.with_suffix(".review.json").write_text(json.dumps(review()), encoding="utf-8")
            before = path.read_bytes()
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = benchmark.main([str(path), "--json"])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output.getvalue())[0]["rework_turn_count"], 1)
            self.assertEqual(path.read_bytes(), before)

    def test_missing_review_fails_without_automatic_usefulness_guess(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "T17-core.json"
            path.write_text(json.dumps(result()), encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(benchmark.main([str(path)]), 2)

    def test_output_cannot_overwrite_result_or_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "T17-core.json"
            review_path = path.with_suffix(".review.json")
            path.write_text(json.dumps(result()), encoding="utf-8")
            review_path.write_text(json.dumps(review()), encoding="utf-8")
            for output in (path, review_path):
                before = output.read_bytes()
                with self.subTest(output=output), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(benchmark.main([str(path), "--out", str(output)]), 2)
                self.assertEqual(output.read_bytes(), before)

    def test_empty_run_has_no_measured_cli_time(self):
        data = result()
        data["turns"] = []
        report = benchmark.summarize(data, review(first_useful_turn=None, rework_turns=[]))
        self.assertIsNone(report["total_cli_seconds"])
        self.assertFalse(report["timing_complete"])


if __name__ == "__main__":
    unittest.main()
