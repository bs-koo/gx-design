"""Regression tests for evaluator isolation, accounting and process cleanup."""
import argparse
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "evals" / filename)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


runner = load_module("hardened_runner", "run_eval.py")
score = load_module("hardened_score", "score.py")
DECISION = {"id": "direction", "type": "selection", "scope_version": "v1"}


def scenario(**extra):
    data = {"id": "case", "skill": "gx-design", "request": "Audit the fixture",
            "mode": "core", "max_turns": 3, "expected": ["Preserve the source"],
            "dialogue": {"version": 1, "checkpoints": []}}
    data.update(extra)
    return data


class IsolationTests(unittest.TestCase):
    def test_fixture_traversal_is_rejected_before_any_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "repo"
            source.mkdir()
            (source / "fixture.txt").write_text("REPLACED")
            keep = root / "keep.txt"
            keep.write_text("KEEP")
            data = scenario(fixtures=[{"src": "fixture.txt", "dest": "../keep.txt"}])
            with patch.object(runner, "REPO_ROOT", source):
                with self.assertRaises(runner.ScenarioError):
                    runner.prepare_workdir(data, root / "work")
            self.assertEqual(keep.read_text(), "KEEP")
            self.assertFalse((root / "work").exists())

    def test_all_fixture_paths_are_checked_before_first_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "repo"
            source.mkdir()
            (source / "fixture.txt").write_text("source")
            data = scenario(fixtures=[{"src": "fixture.txt"},
                                      {"src": "fixture.txt", "dest": "../escape"}])
            with patch.object(runner, "REPO_ROOT", source):
                with self.assertRaises(runner.ScenarioError):
                    runner.prepare_workdir(data, root / "work")
            self.assertFalse((root / "work").exists())

    def test_invalid_fixture_path_forms_fail_schema_validation(self):
        for field in ("src", "dest"):
            for invalid in (None, 17, "", "../outside", "nested/../../outside",
                            "/outside", "C:\\outside", "C:outside", "\\outside"):
                fixture = {"src": "tests/fixtures/eval-ui.html", field: invalid}
                with self.subTest(field=field, value=invalid):
                    with self.assertRaises(runner.ScenarioError):
                        runner.validate_scenario(scenario(fixtures=[fixture]))

    def test_source_symlink_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            outside = root / "outside.txt"
            outside.write_text("private")
            try:
                (repo / "linked.txt").symlink_to(outside)
            except OSError:
                self.skipTest("Creating symlinks requires host privileges")
            with patch.object(runner, "REPO_ROOT", repo):
                with self.assertRaises(runner.ScenarioError):
                    runner.prepare_workdir(scenario(fixtures=[{"src": "linked.txt"}]), root / "work")
            self.assertFalse((root / "work").exists())

    def test_scenario_id_is_a_safe_filename_component(self):
        for invalid in ("../escape", "folder/case", "folder\\case", "C:case", "/case",
                        ".", "..", "CON", "nul.txt", "case.", "case "):
            with self.subTest(id=invalid), self.assertRaises(runner.ScenarioError):
                runner.validate_scenario(scenario(id=invalid))

    @unittest.skipUnless(os.name == "nt", "Windows junction regression")
    def test_nested_junction_cannot_copy_outside_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, outside = root / "repo", root / "outside"
            fixture = repo / "fixture"
            fixture.mkdir(parents=True)
            outside.mkdir()
            (outside / "sentinel.txt").write_text("PRIVATE")
            link = fixture / "junction"
            created = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)],
                                     capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.assertEqual(created.returncode, 0, created.stderr.decode("utf-8", "replace"))
            with patch.object(runner, "REPO_ROOT", repo):
                with self.assertRaises(runner.ScenarioError):
                    runner.prepare_workdir(scenario(fixtures=[{"src": "fixture"}]), root / "work")
            self.assertFalse((root / "work").exists())
            self.assertEqual((outside / "sentinel.txt").read_text(), "PRIVATE")

    def test_result_symlink_cannot_overwrite_an_external_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run = root / "run"
            run.mkdir()
            keep = root / "keep.txt"
            keep.write_text("KEEP")
            try:
                (run / "case-core.json").symlink_to(keep)
            except OSError:
                self.skipTest("Creating symlinks requires host privileges")
            args = make_args(root)
            with patch.object(runner, "_run_turn", side_effect=complete_turn):
                with self.assertRaises(runner.ScenarioError):
                    runner.run_scenario(scenario(), "core", args, run)
            self.assertEqual(keep.read_text(), "KEEP")
            self.assertFalse((run / "work").exists())


def make_args(root):
    return argparse.Namespace(workdir=None, max_turns=0, codex_home=None, dry_run=False,
                              codex_bin="codex", sandbox="workspace-write",
                              results_dir=str(root), timeout=10)


def emit_turn(prompt, cwd, state, session="same-session", usage=None):
    nonce = prompt.split("GX_EVAL_NONCE=", 1)[1].splitlines()[0]
    (cwd / runner.STATE_FILE).write_text(json.dumps({
        "protocol": runner.PROTOCOL, "nonce": nonce, **state}), encoding="utf-8")
    events = [{"type": "thread.started", "thread_id": session}]
    if usage is not None:
        events.append({"type": "turn.completed", "usage": usage})
    return 0, "\n".join(map(json.dumps, events)), ""


def complete_turn(cmd, prompt, env, cwd, timeout):
    return emit_turn(prompt, cwd, {"state": "completed", "pending": []})


class UsageAndSessionTests(unittest.TestCase):
    def test_input_only_usage_keeps_missing_output_explicit(self):
        gaps = runner.usage_observation_gaps([{"input_tokens": 10}, {"input_tokens": 20}])
        self.assertTrue(gaps["usage_incomplete"])
        self.assertEqual(gaps["usage_missing_keys"], [
            {"turn": 1, "keys": ["output_tokens"]}, {"turn": 2, "keys": ["output_tokens"]}])

    def test_all_missing_usage_records_required_keys_as_unknown(self):
        gaps = runner.usage_observation_gaps([{}, {}])
        self.assertTrue(gaps["usage_incomplete"])
        self.assertEqual(gaps["usage_missing_turns"], [1, 2])
        self.assertEqual(gaps["usage_missing_keys"], [
            {"turn": 1, "keys": ["input_tokens", "output_tokens"]},
            {"turn": 2, "keys": ["input_tokens", "output_tokens"]}])

    def test_optional_host_usage_keys_need_not_be_emitted(self):
        gaps = runner.usage_observation_gaps([{"input_tokens": 10, "output_tokens": 2}])
        self.assertFalse(gaps["usage_incomplete"])

    def test_missing_last_usage_preserves_known_totals(self):
        _, total, mode = runner.aggregate_turn_usage([
            {"input_tokens": 100, "cached_input_tokens": 60, "output_tokens": 10}, {}])
        self.assertEqual(mode, "cumulative")
        self.assertEqual(total, {"input_tokens": 100, "cached_input_tokens": 60,
                                 "output_tokens": 10, "uncached_input_tokens": 40})

    def test_usage_gaps_preserve_each_key_and_delta_baseline(self):
        deltas, total, _ = runner.aggregate_turn_usage([
            {"input_tokens": 100, "output_tokens": 10}, {}, {"input_tokens": 150}])
        self.assertEqual(deltas, [{"input_tokens": 100, "output_tokens": 10}, {}, {"input_tokens": 50}])
        self.assertEqual(total["output_tokens"], 10)

    def test_missing_usage_is_reported_without_changing_completion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cp = {"decision": DECISION, "response": {"status": "answered", "value": "A"}}
            data = scenario(dialogue={"version": 1, "checkpoints": [cp]})
            calls = []

            def turn(cmd, prompt, env, cwd, timeout):
                index = len(calls)
                calls.append(prompt)
                state = ({"state": "waiting", "pending": [dict(DECISION, required=True, status="unresolved")]}
                         if index == 0 else {"state": "completed", "pending": []})
                return emit_turn(prompt, cwd, state, usage={"input_tokens": 100} if index == 0 else None)

            with patch.object(runner, "_run_turn", side_effect=turn), contextlib.redirect_stdout(io.StringIO()):
                result = runner.run_scenario(data, "core", make_args(root), root / "run")
            self.assertEqual(result["stop_reason"], "completed")
            self.assertIn("input_tokens", result["usage"])
            self.assertEqual(result["usage"]["input_tokens"], 100)
            self.assertTrue(result["usage_incomplete"])
            self.assertEqual(result["usage_missing_turns"], [2])
            row = score.load_row(root / "run" / "case-core.json")
            table = score.aggregate([row])
            self.assertEqual(table[0]["usage_incomplete_n"], 1)
            self.assertIn("사용량 일부 누락", score.format_table(table))

    def test_resume_session_mismatch_stops_before_next_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cp = {"decision": DECISION, "response": {"status": "answered", "value": "A"}}
            data = scenario(dialogue={"version": 1, "checkpoints": [cp, cp]})
            calls = []

            def turn(cmd, prompt, env, cwd, timeout):
                calls.append(prompt)
                return emit_turn(prompt, cwd, {"state": "waiting", "pending": [
                    dict(DECISION, required=True, status="unresolved")]}, session=f"session-{len(calls)}")

            with patch.object(runner, "_run_turn", side_effect=turn), contextlib.redirect_stdout(io.StringIO()):
                result = runner.run_scenario(data, "core", make_args(root), root / "run")
            self.assertEqual(result["stop_reason"], "session_mismatch")
            self.assertEqual(len(calls), 2)
            self.assertEqual(result["checkpoints_dispatched"], 1)
            self.assertFalse(result["eligible_for_success_average"])


class ScoreOutcomeTests(unittest.TestCase):
    def test_expected_waiting_and_stopped_outcomes_keep_their_scores(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for reason in ("waiting", "stopped"):
                with self.subTest(reason=reason):
                    path = root / f"{reason}.json"
                    path.write_text(json.dumps({"scenario": reason, "mode": "core", "stop_reason": reason}))
                    score.score_path_for(path).write_text(json.dumps({
                        "scores": {"gate_compliance": 2},
                        "dialogue": {"dependent_work_wait": 2, "scope_preservation": 2},
                        "artifact": {"task_success": 0}}))
                    table = score.aggregate([score.load_row(path)])
                    self.assertEqual(table[0]["n"], 0)
                    self.assertEqual(table[0]["dialogue"], {"got": 4, "max": 4, "n": 1})
                    self.assertEqual(table[0]["artifact"], {"got": 0, "max": 2, "n": 1})
                    text = score.format_table(table)
                    self.assertIn("완료 비용 표본 수", text)
                    self.assertIn("2/2 (n=1)", text)
                    self.assertIn("4/4", text)
                    self.assertIn("0/2", text)
                    self.assertIn("2/2", text)


class ProcessCleanupTests(unittest.TestCase):
    def test_normal_exit_with_inherited_child_output_is_not_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            child = "import time;time.sleep(10)"
            parent = ("import subprocess,sys; "
                      f"subprocess.Popen([sys.executable,'-c',{child!r}]); "
                      "print('parent finished',flush=True)")
            code, out, err = runner._run_turn([sys.executable, "-c", parent], "", dict(os.environ), Path(tmp), 3)
            self.assertEqual(code, 0, err)
            self.assertIn("parent finished", out)
            self.assertNotIn("[timeout", err)

    def test_normal_exit_cleans_up_surviving_descendants(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            started, release, mutation = (root / name for name in ("started.json", "release", "late-write.txt"))
            child = ("import json,os,pathlib,time; "
                     f"pathlib.Path({str(started)!r}).write_text(json.dumps({{'pid':os.getpid()}})); "
                     f"release=pathlib.Path({str(release)!r}); deadline=time.monotonic()+12\n"
                     "while not release.exists() and time.monotonic()<deadline: time.sleep(.02)\n"
                     f"if release.exists(): pathlib.Path({str(mutation)!r}).write_text('continued')\n")
            parent = ("import pathlib,subprocess,sys,time; "
                      f"subprocess.Popen([sys.executable,'-c',{child!r}],"
                      "stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); "
                      f"started=pathlib.Path({str(started)!r}); deadline=time.monotonic()+5\n"
                      "while not started.exists() and time.monotonic()<deadline: time.sleep(.02)\n")
            child_pid = None
            try:
                code, _, _ = runner._run_turn([sys.executable, "-c", parent], "", dict(os.environ), root, 10)
                self.assertEqual(code, 0)
                self.assertTrue(started.exists())
                child_pid = json.loads(started.read_text())["pid"]
                release.write_text("go")
                time.sleep(.35)
                self.assertFalse(mutation.exists(), "Descendant survived normal CLI completion")
            finally:
                if child_pid is None and started.exists():
                    child_pid = json.loads(started.read_text())["pid"]
                if child_pid:
                    try:
                        os.kill(child_pid, signal.SIGTERM)
                    except (ProcessLookupError, PermissionError):
                        pass

    def test_timeout_stops_descendants_before_returning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            started = root / "started.json"
            release = root / "release"
            mutation = root / "late-write.txt"
            # The descendant writes only if it survives _run_turn returning and release.
            child = ("import json,os,pathlib,time; "
                     f"pathlib.Path({str(started)!r}).write_text(json.dumps({{'pid':os.getpid()}})); "
                     f"release=pathlib.Path({str(release)!r}); "
                     f"mutation=pathlib.Path({str(mutation)!r}); "
                     "deadline=time.monotonic()+12\n"
                     "while not release.exists() and time.monotonic()<deadline: time.sleep(.02)\n"
                     "if release.exists(): mutation.write_text('continued')\n")
            parent = ("import subprocess,sys,time; "
                      f"subprocess.Popen([sys.executable,'-c',{child!r}],"
                      "stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(20)")
            child_pid = None
            try:
                code, _, stderr = runner._run_turn([sys.executable, "-c", parent], "", dict(os.environ), root, 3)
                self.assertEqual(code, -1)
                self.assertIn("timeout", stderr)
                self.assertTrue(started.exists(), "The real descendant must start before timeout")
                child_pid = json.loads(started.read_text())["pid"]
                release.write_text("go")
                time.sleep(.35)
                self.assertFalse(mutation.exists(), "Descendant changed files after timeout returned")
            finally:
                if child_pid is None and started.exists():
                    child_pid = json.loads(started.read_text())["pid"]
                if child_pid:
                    try:
                        os.kill(child_pid, signal.SIGTERM)
                    except (ProcessLookupError, PermissionError):
                        pass

    def test_success_preserves_stdin_stdout_stderr_and_exit_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            command = [sys.executable, "-c", "import sys; sys.stdin.reconfigure(encoding='utf-8'); sys.stdout.reconfigure(encoding='utf-8'); print(sys.stdin.read()); print('diagnostic',file=sys.stderr); sys.exit(7)"]
            code, stdout, stderr = runner._run_turn(command, "한글 prompt", dict(os.environ), Path(tmp), 10)
            self.assertEqual(code, 7)
            self.assertEqual(stdout.strip(), "한글 prompt")
            self.assertIn("diagnostic", stderr)


if __name__ == "__main__":
    unittest.main()
