"""Deterministic harness tests; these do not measure real model quality."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "evals" / filename)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


runner = module("dialogue_runner", "run_eval.py")
score = module("dialogue_score", "score.py")
DECISION = {"id": "direction", "type": "selection", "scope_version": "v1"}


def scenario(checkpoints=None, **extra):
    result = {"id": "case", "skill": "gx-design", "request": "Make the approved page",
              "mode": "core", "answers": ["Unrelated old approval"], "max_turns": 5,
              "expected": ["Only matched answers may be sent"],
              "dialogue": {"version": 1, "checkpoints": checkpoints or []}}
    result.update(extra)
    return result


def checkpoint(decision=None, status="answered", value="Use A"):
    return {"decision": decision or DECISION, "response": {"status": status, "value": value}}


def signal(state="waiting", pending=None, **extra):
    return {"state": state, "pending": ([dict(DECISION, required=True, status="unresolved")]
                                        if pending is None else pending), **extra}


class DialogueRunnerTests(unittest.TestCase):
    def run_case(self, data, signals, mutation=None, events=None):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            args = argparse.Namespace(workdir=None, max_turns=0, codex_home=None,
                                      dry_run=False, codex_bin="codex", sandbox="workspace-write",
                                      results_dir=str(base), timeout=1)
            calls = []

            def turn(cmd, prompt, env, cwd, timeout):
                index = len(calls)
                calls.append(prompt)
                if mutation:
                    mutation(cwd, index)
                state = signals[min(index, len(signals) - 1)]
                if state is not None:
                    # Mock the evaluator sidecar emitted by a model/tool adapter.
                    nonce = prompt.split("GX_EVAL_NONCE=", 1)[1].splitlines()[0] if "GX_EVAL_NONCE=" in prompt else "old-runner"
                    payload = {"protocol": "gx-eval-dialogue/v1", "nonce": nonce, **state}
                    (cwd / ".gx-eval-state.json").write_text(json.dumps(payload), encoding="utf-8")
                stream = [{"type": "thread.started", "thread_id": "same-session"},
                          {"type": "item.completed", "item": {"type": "agent_message", "text": "Done, no question."}}]
                stream.extend(events or [])
                return 0, "\n".join(map(json.dumps, stream)), ""

            with patch.object(runner, "_run_turn", side_effect=turn):
                result = runner.run_scenario(data, "core", args, base / "run")
            return result, calls

    def test_completion_does_not_inject_remaining_approval(self):
        result, calls = self.run_case(scenario([checkpoint()]), [signal("completed", [])])
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["stop_reason"], "completed")

    def test_unexpected_pending_question_does_not_receive_fixed_answer(self):
        other = dict(DECISION, id="budget", required=True, status="unresolved")
        result, calls = self.run_case(scenario([checkpoint()]), [signal(pending=[other])])
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["stop_reason"], "unexpected_question")

    def test_matched_checkpoint_then_questionless_completion(self):
        result, calls = self.run_case(scenario([checkpoint()]), [signal(), signal("completed", [])])
        self.assertEqual(len(calls), 2)
        self.assertIn("Use A", calls[1])
        self.assertNotIn("Unrelated old approval", calls[1])
        self.assertTrue(result["eligible_for_success_average"])

    def test_missing_signal_never_uses_prose_as_approval(self):
        result, calls = self.run_case(scenario([checkpoint()]), [None])
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["stop_reason"], "missing_signal")

    def test_stale_scope_is_not_matched(self):
        result, calls = self.run_case(scenario([checkpoint(dict(DECISION, scope_version="v0"))]), [signal()])
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["stop_reason"], "unexpected_question")

    def test_wrong_decision_type_is_not_matched(self):
        result, calls = self.run_case(scenario([checkpoint(dict(DECISION, type="approval"))]), [signal()])
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["stop_reason"], "unexpected_question")

    def test_stale_nonce_cannot_reuse_previous_question_signal(self):
        result, calls = self.run_case(scenario([checkpoint()]), [signal(), None])
        self.assertEqual(len(calls), 2)
        self.assertEqual(result["stop_reason"], "stale_or_invalid_signal")

    def test_partial_reply_cannot_complete_by_dropping_pending_decisions(self):
        for status in ("partial", "empty", "cancelled", "status_query"):
            with self.subTest(status=status):
                result, _ = self.run_case(scenario([checkpoint(status=status, value=None)]),
                                          [signal(), signal("completed", [])])
                self.assertEqual(result["stop_reason"], "unresolved_required")

    def test_answering_one_of_three_does_not_resolve_other_two(self):
        pending = [dict(DECISION, id=name, required=True, status="unresolved")
                   for name in ("direction", "target", "artifact")]
        result, _ = self.run_case(scenario([checkpoint()]),
                                  [signal(pending=pending), signal("completed", [])])
        self.assertEqual(result["stop_reason"], "unresolved_required")

    def test_model_invalidation_cannot_clear_non_authorizing_responses(self):
        for status in ("empty", "partial", "cancelled", "status_query", "rejected"):
            with self.subTest(status=status):
                invalidated = dict(DECISION, reason="Assumed user no longer needed this")
                result, _ = self.run_case(scenario([checkpoint(status=status, value=None)]),
                                          [signal(), signal("completed", [], invalidated=[invalidated])])
                self.assertEqual(result["stop_reason"], "unauthorized_invalidation")
                self.assertFalse(result["eligible_for_success_average"])
                self.assertEqual(result["outstanding_required"], [DECISION])

    def test_explicit_scripted_scope_invalidation_does_not_inject_another_approval(self):
        invalidated = dict(DECISION, reason="User withdrew this direction decision")
        response = checkpoint(status="scope_change", value="Drop the direction selection; audit only.")
        response["response"]["invalidates"] = [invalidated]
        result, calls = self.run_case(scenario([response]),
                                      [signal(), signal("completed", [], invalidated=[invalidated])])
        self.assertEqual(len(calls), 2)
        self.assertEqual(result["stop_reason"], "completed")

    def test_authorized_invalidation_cannot_expand_identity_or_reason(self):
        invalidated = dict(DECISION, reason="User withdrew this direction decision")
        response = checkpoint(status="scope_change", value="Drop only this selection.")
        response["response"]["invalidates"] = [invalidated]
        for modified in (dict(invalidated, scope_version="v2"), dict(invalidated, type="approval"),
                         dict(invalidated, id="other"), dict(invalidated, reason="Model invented reason")):
            with self.subTest(invalidation=modified):
                result, _ = self.run_case(scenario([response]),
                                          [signal(), signal("completed", [], invalidated=[modified])])
                self.assertEqual(result["stop_reason"], "unauthorized_invalidation")

    def test_elapsed_seconds_use_monotonic_turn_and_total_clocks(self):
        with patch.object(runner.time, "perf_counter", side_effect=[10, 11, 13.5, 14, 18, 21]):
            result, _ = self.run_case(scenario([checkpoint()]), [signal(), signal("completed", [])])
        self.assertEqual([turn["elapsed_seconds"] for turn in result["turns"]], [2.5, 4])
        self.assertEqual(result["elapsed_seconds"], 11)
        self.assertEqual(result["turn_elapsed_seconds"], 6.5)

    def test_bad_signal_types_stop_safely(self):
        for bad_state in (signal(state=[]), signal(pending=[dict(DECISION, required=True, status=[])])):
            with self.subTest(state=bad_state):
                result, calls = self.run_case(scenario([checkpoint()]), [bad_state])
                self.assertEqual(len(calls), 1)
                self.assertEqual(result["stop_reason"], "invalid_signal")

    def test_partial_empty_cancel_status_replies_do_not_resolve_other_questions(self):
        for status, value in [("partial", "A"), ("empty", None), ("cancelled", None),
                              ("status_query", "Where are we?")]:
            with self.subTest(status=status):
                result, calls = self.run_case(scenario([checkpoint(status=status, value=value)]),
                                              [signal(), signal()])
                self.assertEqual(len(calls), 2)
                self.assertEqual(result["stop_reason"], "waiting")
                self.assertFalse(result["eligible_for_success_average"])

    def test_completion_with_unresolved_required_decision_is_invalid(self):
        result, _ = self.run_case(scenario(), [signal("completed")])
        self.assertEqual(result["stop_reason"], "invalid_signal")

    def test_max_turns_excludes_run(self):
        result, calls = self.run_case(scenario([checkpoint()], max_turns=1), [signal()])
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["stop_reason"], "max_turns")
        self.assertFalse(result["eligible_for_success_average"])

    def test_legacy_answers_are_visible_but_not_blindly_injected(self):
        data = scenario()
        del data["dialogue"]
        result, calls = self.run_case(data, [signal()])
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["stop_reason"], "legacy_unbound_answers")
        self.assertIn("legacy", result["dialogue_format"])

    def test_content_hash_detects_same_size_and_timestamp_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "artifact.txt"
            path.write_text("before")
            initial = path.stat()
            before = runner.snapshot(Path(tmp))
            path.write_text("after!")
            os.utime(path, ns=(initial.st_atime_ns, initial.st_mtime_ns))
            after = runner.snapshot(Path(tmp))
            self.assertEqual(runner.changed_files(before, after)["modified"], ["artifact.txt"])

    def test_in_turn_reverted_change_events_are_preserved(self):
        events = [{"type": "item.completed", "item": {"type": "file_change", "changes": [{"path": "original.html", "kind": "update"}]}},
                  {"type": "item.completed", "item": {"type": "command_execution", "command": "write then restore", "exit_code": 0}}]
        result, _ = self.run_case(scenario(), [signal("completed", [])], events=events)
        turn = result["turns"][0]
        self.assertEqual(len(turn["mutation_events"]), 2)
        self.assertEqual(turn["files"], {"created": [], "modified": [], "deleted": []})
        self.assertIn("shell", result["observation_limits"])
        self.assertIn("file_hashes_before", turn)


class EvaluationScoreTests(unittest.TestCase):
    def test_incomplete_and_legacy_excluded_from_success_averages(self):
        rows = [{"scenario": "s", "mode": "core", "stop_reason": reason,
                 "turns": 1, "tool_calls": 0, "usage": {k: 0 for k in score.USAGE_COLUMNS}, "rubric": None}
                for reason in ("completed", "max_turns", "waiting", "unexpected_question", "answers_exhausted", "")]
        table = score.aggregate(rows)
        self.assertEqual(table[0]["n"], 1)
        self.assertEqual(len(table[0]["excluded"]), 5)

    def test_old_scores_and_new_dimensions_remain_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_path = Path(tmp) / "case.json"
            result_path.write_text(json.dumps({"scenario": "case", "mode": "core", "stop_reason": "completed"}))
            score.score_path_for(result_path).write_text(json.dumps({
                "scores": {"gate_compliance": 2},
                "dialogue": {"required_intent": 1, "scope_preservation": 2},
                "artifact": {"task_success": 0, "verification_coverage": None}}))
            row = score.load_row(result_path)
            self.assertEqual(row["rubric"]["got"], 2)
            table = score.aggregate([row])[0]
            self.assertEqual(table["dialogue"], {"got": 3, "max": 4, "n": 1})
            self.assertEqual(table["artifact"], {"got": 0, "max": 2, "n": 1})


class AcceptanceFixtureTests(unittest.TestCase):
    def test_all_21_acceptance_cases_are_valid_explicitly_unexecuted(self):
        cases = runner.load_scenarios(ROOT / "evals" / "dialogue-scenarios")
        self.assertEqual({c["id"] for c in cases}, {f"T{i:02d}" for i in range(1, 22)})
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertIn("dialogue", case)
                self.assertEqual(case["answers"], [])
                self.assertEqual(case["validation_status"], "unexecuted-model-acceptance")
                self.assertTrue(case["expected"])

    def test_legacy_schema_has_no_implicit_dialogue_migration(self):
        cases = runner.load_scenarios(ROOT / "evals" / "scenarios")
        self.assertEqual(len(cases), 4)
        self.assertTrue(all("dialogue" not in case for case in cases))

    def test_invalid_checkpoint_cannot_carry_empty_approval(self):
        with self.assertRaises(runner.ScenarioError):
            runner.validate_scenario(scenario([checkpoint(value="")]))

    def test_invalid_response_type_and_version_raise_scenario_error(self):
        for invalid in (scenario([checkpoint(status=[])]),
                        scenario(dialogue={"version": 1.0, "checkpoints": []})):
            with self.subTest(data=invalid), self.assertRaises(runner.ScenarioError):
                runner.validate_scenario(invalid)

    def test_only_explicit_scope_change_can_supply_invalidation_authority(self):
        for status in ("empty", "partial", "cancelled", "status_query", "answered", "delegated"):
            response = checkpoint(status=status, value="not a scope change")
            response["response"]["invalidates"] = [dict(DECISION, reason="withdraw")]
            with self.subTest(status=status), self.assertRaises(runner.ScenarioError):
                runner.validate_scenario(scenario([response]))

    def test_default_results_workdir_is_allowed_but_other_repo_paths_are_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            results = repo / "evals" / "results"
            runner.validate_workdir(results / "run" / "work" / "T11", results, repo)
            with self.assertRaises(runner.ScenarioError):
                runner.validate_workdir(repo / "source", results, repo)


if __name__ == "__main__":
    unittest.main()
