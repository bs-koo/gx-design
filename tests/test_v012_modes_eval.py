import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run_eval = load_module("gx_eval_run_eval", EVALS / "run_eval.py")
score = load_module("gx_eval_score", EVALS / "score.py")


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


READ_MAP_DOCS = tuple(
    f"skills/gx-design/{name}.md"
    for name in ("VISUAL-CRAFT", "VISUAL-QUALITY", "MOTION", "UI-QUALITY", "ANTI-TELL-CHECKLIST", "PROMPT-PLAYBOOK")
)

# 스펙 §3 필수 앵커 (docs/superpowers/specs/2026-10-15-v012-modes-outcome-eval-design.md)
ANCHORS = {
    "skills/gx-design/RUN-BUDGET.md": ("## 단계별 승격", "## 비용 기록", "실행량", "화면당 40줄", "외부 출처"),
    "skills/gx-design/DESIGN-IT-TWICE.md": ("스케치", "확장"),
    "skills/gx-design/REVIEW-AXES.md": ("동일 맥락 검수", "축 B"),
    "skills/gx-design/SKILL.md": ("RUN-BUDGET.md", "스케치"),
    "skills/gx-redesign/SKILL.md": ("RUN-BUDGET.md", "스케치"),
    "skills/gx-design/UI-QUALITY.md": ("IA·과업 흐름", "상태 ID", "휴리스틱 추정", "접근성 트리", "LCP"),
    "skills/gx-design/VISUAL-QUALITY.md": ("320px", "경로 ID"),
    "skills/gx-redesign/REDESIGN-INTERVIEW.md": ("기준선", "기준 ID"),
    "skills/creative-review/SKILL.md": ("재측정",),
}
for _path in READ_MAP_DOCS:
    ANCHORS[_path] = ANCHORS.get(_path, ()) + ("읽기 지도",)

# Codex exec --json 형식을 흉내 낸 합성 이벤트(알 수 없는 이벤트와 깨진 줄 포함).
SAMPLE_JSONL = "\n".join(
    [
        json.dumps({"type": "thread.started", "thread_id": "019a-thread-abc"}),
        json.dumps({"type": "turn.started"}),
        json.dumps({"type": "item.started", "item": {"id": "item_0", "type": "command_execution", "command": "ls"}}),
        json.dumps({"type": "item.completed", "item": {"id": "item_0", "type": "command_execution", "exit_code": 0}}),
        json.dumps({"type": "item.completed", "item": {"id": "item_1", "type": "reasoning", "text": "..."}}),
        json.dumps({"type": "item.completed", "item": {"id": "item_2", "type": "file_change", "changes": []}}),
        json.dumps({"type": "item.started", "item": {"id": "item_3", "type": "mcp_tool_call"}}),
        json.dumps({"type": "item.completed", "item": {"id": "item_4", "type": "agent_message", "text": "첫 질문"}}),
        json.dumps({"type": "something.new", "payload": {"x": 1}}),
        "not json at all",
        json.dumps({"type": "turn.completed", "usage": {
            "input_tokens": 1000, "cached_input_tokens": 400, "output_tokens": 120, "reasoning_output_tokens": 30}}),
        json.dumps({"type": "turn.completed", "usage": {"input_tokens": 500, "output_tokens": 80, "flag": True}}),
        "",
    ]
)


def valid_scenario(**overrides) -> dict:
    data = {
        "id": "t",
        "skill": "gx-design",
        "request": "랜딩",
        "mode": "core",
        "answers": ["추천안대로 진행"],
        "max_turns": 3,
        "expected": ["승인 전 산출물 0"],
    }
    data.update(overrides)
    return data


class EventParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.events, self.junk = run_eval.parse_jsonl(SAMPLE_JSONL)

    def test_parse_jsonl_keeps_unknown_events_and_counts_junk(self) -> None:
        self.assertEqual(len(self.events), 11)
        self.assertEqual(self.junk, ["not json at all"])

    def test_usage_sums_all_numeric_keys(self) -> None:
        usage = run_eval.sum_usage(self.events)
        self.assertEqual(
            usage,
            {"input_tokens": 1500, "cached_input_tokens": 400, "output_tokens": 200, "reasoning_output_tokens": 30},
        )

    def test_legacy_cumulative_usage_fallback(self) -> None:
        events = [
            {"id": "0", "msg": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": 10}}}},
            {"id": "1", "msg": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": 25}}}},
        ]
        self.assertEqual(run_eval.sum_usage(events), {})
        self.assertEqual(run_eval.summarize_events(events)["usage"], {"input_tokens": 25})

    def test_tool_counts_by_type_without_double_counting(self) -> None:
        counts = run_eval.count_tools(self.events)
        self.assertEqual(counts, {"command_execution": 1, "file_change": 1, "mcp_tool_call": 1})

    def test_legacy_tool_events_are_counted(self) -> None:
        events = [
            {"id": "1", "msg": {"type": "exec_command_begin"}},
            {"id": "1", "msg": {"type": "exec_command_end"}},
            {"id": "2", "msg": {"type": "mcp_tool_call_begin"}},
        ]
        self.assertEqual(run_eval.count_tools(events), {"exec_command_begin": 1, "mcp_tool_call_begin": 1})

    def test_summary_has_last_agent_message(self) -> None:
        summary = run_eval.summarize_events(self.events)
        self.assertEqual(summary["last_message"], "첫 질문")
        self.assertEqual(summary["event_types"]["something.new"], 1)


class SessionIdTests(unittest.TestCase):
    def test_thread_started_event(self) -> None:
        events, _ = run_eval.parse_jsonl(SAMPLE_JSONL)
        self.assertEqual(run_eval.extract_session_id(events), "019a-thread-abc")

    def test_only_documented_thread_id_is_accepted(self) -> None:
        events = [{"id": "0", "msg": {"type": "session_configured", "session_id": "sess-1", "model": "x"}}]
        self.assertIsNone(run_eval.extract_session_id(events))

    def test_start_event_with_nested_id(self) -> None:
        events = [{"type": "thread.started", "thread_id": "thread-7", "session": {"id": "nested-7"}}]
        self.assertEqual(run_eval.extract_session_id(events), "thread-7")

    def test_fallback_and_missing(self) -> None:
        self.assertIsNone(run_eval.extract_session_id([{"type": "turn.started", "thread_id": "fb"}]))
        self.assertIsNone(run_eval.extract_session_id([{"type": "turn.started"}]))

    def test_resume_stream_id_mismatch_is_detected(self) -> None:
        original, resumed = "thread-1", "thread-2"
        self.assertNotEqual(original, resumed)


class UsageAggregationTests(unittest.TestCase):
    def test_cumulative_turn_usage_uses_last_total_and_deltas(self) -> None:
        samples = [
            {"input_tokens": 975558, "cached_input_tokens": 900480, "cache_write_input_tokens": 0, "output_tokens": 7439, "reasoning_output_tokens": 706},
            {"input_tokens": 1066567, "cached_input_tokens": 985728, "cache_write_input_tokens": 0, "output_tokens": 7685, "reasoning_output_tokens": 854},
            {"input_tokens": 1159958, "cached_input_tokens": 1076608, "cache_write_input_tokens": 0, "output_tokens": 7718, "reasoning_output_tokens": 854},
        ]
        deltas, total, mode = run_eval.aggregate_turn_usage(samples)
        self.assertEqual(mode, "cumulative")
        self.assertEqual(total["input_tokens"], 1159958)
        self.assertEqual(total["output_tokens"], 7718)
        self.assertEqual(total["uncached_input_tokens"], 83350)
        self.assertEqual([row["input_tokens"] for row in deltas], [975558, 91009, 93391])

    def test_non_monotonic_usage_falls_back_to_sum(self) -> None:
        _, total, mode = run_eval.aggregate_turn_usage([{"input_tokens": 8}, {"input_tokens": 5}])
        self.assertEqual(mode, "summed")
        self.assertEqual(total["input_tokens"], 13)


class WorkdirSafetyTests(unittest.TestCase):
    def test_non_empty_or_repo_nested_workdir_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            results = root / "evals" / "results"
            nested = root / "nested"
            nested.mkdir()
            with self.assertRaises(run_eval.ScenarioError):
                run_eval.validate_workdir(nested, results, root)
            external = Path(tmp) / "external"
            external.mkdir()
            (external / "keep.txt").write_text("x")
            with self.assertRaises(run_eval.ScenarioError):
                run_eval.prepare_workdir(valid_scenario(), external)


class ScenarioLoaderTests(unittest.TestCase):
    def test_valid_scenario_gets_defaults(self) -> None:
        scenario = run_eval.validate_scenario(valid_scenario())
        self.assertEqual(scenario["fixtures"], [])
        self.assertEqual(scenario["title"], "t")

    def test_missing_required_key_is_rejected(self) -> None:
        for key in run_eval.REQUIRED_KEYS:
            data = valid_scenario()
            del data[key]
            with self.subTest(key=key), self.assertRaises(run_eval.ScenarioError):
                run_eval.validate_scenario(data)

    def test_bad_values_are_rejected(self) -> None:
        for override in (
            {"skill": "other"},
            {"mode": "fast"},
            {"answers": [""]},
            {"answers": "추천안"},
            {"max_turns": 0},
            {"max_turns": True},
            {"expected": []},
            {"fixtures": [{"dest": "x"}]},
        ):
            with self.subTest(override=override), self.assertRaises(run_eval.ScenarioError):
                run_eval.validate_scenario(valid_scenario(**override))

    def test_load_scenario_from_file_and_bad_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "good.json"
            good.write_text(json.dumps(valid_scenario(), ensure_ascii=False), encoding="utf-8")
            bad = Path(tmp) / "bad.json"
            bad.write_text("{not json", encoding="utf-8")
            self.assertEqual(run_eval.load_scenario(good)["id"], "t")
            with self.assertRaises(run_eval.ScenarioError):
                run_eval.load_scenario(bad)

    def test_commands_use_stdin_prompt_and_resume_id(self) -> None:
        start = run_eval.build_start_command("codex", Path("w"), "workspace-write")
        self.assertEqual(start[:3], ["codex", "exec", "--json"])
        self.assertIn("-C", start)
        self.assertEqual(start[-1], "-")
        resume = run_eval.build_resume_command("codex", "sid-1", "workspace-write")
        self.assertEqual(resume[:3], ["codex", "exec", "resume"])
        self.assertEqual(resume[-2:], ["sid-1", "-"])
        prompt = run_eval.build_initial_prompt(run_eval.validate_scenario(valid_scenario()), "core")
        self.assertTrue(prompt.startswith("$gx-design "))
        self.assertIn("핵심 모드", prompt)


class RepositoryScenarioTests(unittest.TestCase):
    def test_evals_files_exist(self) -> None:
        for name in ("README.md", "rubric.md", "run_eval.py", "score.py"):
            with self.subTest(name=name):
                self.assertTrue((EVALS / name).is_file())

    def test_exactly_four_valid_scenarios(self) -> None:
        scenarios = run_eval.load_scenarios(EVALS / "scenarios")
        self.assertEqual(len(scenarios), 4)
        self.assertEqual(len({s["id"] for s in scenarios}), 4)
        self.assertEqual({s["skill"] for s in scenarios}, {"gx-design", "gx-redesign"})

    def test_audit_scenario_copies_site_fixture(self) -> None:
        scenario = run_eval.load_scenario(EVALS / "scenarios/03-site-motion-audit.json")
        self.assertIn("점검", scenario["request"])
        self.assertEqual(scenario["fixtures"][0]["src"], "site/index.html")
        with tempfile.TemporaryDirectory() as tmp:
            copied = run_eval.prepare_workdir(scenario, Path(tmp) / "w")
            self.assertEqual(copied, ["index.html"])

    def test_snapshot_diff(self) -> None:
        before = {"a": (1, 1), "b": (2, 2)}
        after = {"a": (1, 1), "b": (3, 3), "c": (1, 1)}
        self.assertEqual(run_eval.changed_files(before, after), {"created": ["c"], "modified": ["b"], "deleted": []})

    def test_results_are_gitignored(self) -> None:
        self.assertIn("evals/results/", read_doc(".gitignore").splitlines())


class ScoreTests(unittest.TestCase):
    def write_result(self, directory: Path, scenario: str, mode: str, usage: dict, turns: int, tools: int) -> Path:
        path = directory / f"{scenario}-{mode}.json"
        path.write_text(json.dumps({
            "scenario": scenario, "mode": mode, "turn_count": turns, "usage": usage,
            "tool_counts": {"command_execution": tools}, "tool_calls": tools,
        }), encoding="utf-8")
        return path

    def test_aggregate_averages_runs_and_merges_scores(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run1, run2 = Path(tmp) / "r1", Path(tmp) / "r2"
            run1.mkdir()
            run2.mkdir()
            first = self.write_result(run1, "s3", "core", {"input_tokens": 100, "output_tokens": 10}, 3, 4)
            self.write_result(run2, "s3", "core", {"input_tokens": 300, "output_tokens": 30}, 5, 6)
            self.write_result(run1, "s3", "full", {"input_tokens": 900}, 4, 9)
            score.score_path_for(first).write_text(json.dumps({
                "scorer": "x",
                "scores": {"gate_compliance": 2, "slop_avoidance": 1, "motion_violations": None},
            }), encoding="utf-8")
            (run1 / "work").mkdir()
            (run1 / "work" / "package.json").write_text("{broken", encoding="utf-8")

            files = score.collect_result_files([Path(tmp)])
            self.assertEqual(len(files), 3)
            rows = [score.load_row(p) for p in files]
            table = score.aggregate(rows)

        by_key = {(e["scenario"], e["mode"]): e for e in table}
        core = by_key[("s3", "core")]
        self.assertEqual(core["n"], 2)
        self.assertEqual(core["turns"], 4)
        self.assertEqual(core["tool_calls"], 5)
        self.assertEqual(core["usage"]["input_tokens"], 200)
        self.assertEqual(core["usage"]["cached_input_tokens"], 0)
        self.assertEqual(core["usage"]["uncached_input_tokens"], 0)
        self.assertEqual(core["rubric"], {"got": 3, "max": 4, "n": 1})
        self.assertIsNone(by_key[("s3", "full")]["rubric"])

        text = score.format_table(table)
        self.assertIn("| s3 | core | 평균 | 2 | 4 | 200 |", text)
        self.assertIn("3/4", text)
        self.assertIn("미채점", text)

    def test_rubric_total_rejects_out_of_range(self) -> None:
        self.assertEqual(score.rubric_total({k: 2 for k in score.RUBRIC_KEYS}), (12, 12))
        with self.assertRaises(ValueError):
            score.rubric_total({"gate_compliance": 3})

    def test_stopped_runs_excluded_and_reported_separately(self) -> None:
        rows = [
            {"scenario": "s", "mode": "core", "stop_reason": "answers_exhausted", "turns": 2, "tool_calls": 3, "usage": {key: 1 for key in score.USAGE_COLUMNS}, "rubric": None},
            {"scenario": "s", "mode": "core", "stop_reason": "session_mismatch", "turns": 1, "tool_calls": 1, "usage": {key: 99 for key in score.USAGE_COLUMNS}, "rubric": None},
        ]
        table = score.aggregate(rows)
        self.assertEqual(table[0]["n"], 1)
        self.assertEqual(table[0]["excluded"][0]["stop_reason"], "session_mismatch")
        self.assertIn("채점 표본 수", score.format_table(table))

    def test_invalid_scores_file_has_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.write_result(Path(tmp), "s", "core", {}, 1, 1)
            score.score_path_for(result).write_text(json.dumps({"scores": {"gate_compliance": 3}}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r"\.scores\.json 형식 오류"):
                score.load_row(result)

    def test_rubric_doc_lists_all_criteria(self) -> None:
        text = read_doc("evals/rubric.md")
        for key in score.RUBRIC_KEYS:
            with self.subTest(key=key):
                self.assertIn(f"`{key}`", text)


class V012AnchorTests(unittest.TestCase):
    def test_spec_anchor_strings_are_present(self) -> None:
        for relative_path, terms in ANCHORS.items():
            with self.subTest(path=relative_path):
                self.assertTrue((ROOT / relative_path).exists(), f"{relative_path} must exist")
                text = read_doc(relative_path)
                for term in terms:
                    with self.subTest(path=relative_path, term=term):
                        self.assertTrue(term in text, f"{relative_path} must contain {term!r}")

    def test_new_decision_anchors(self) -> None:
        redesign = read_doc("skills/gx-redesign/SKILL.md")
        review = read_doc("skills/gx-design/REVIEW-AXES.md")
        budget = read_doc("skills/gx-design/RUN-BUDGET.md")
        motion = read_doc("skills/gx-design/MOTION.md")
        self.assertIn("[요청에서 확정]", redesign)
        self.assertIn("점검 결과를 보고하고 이어가기 게이트 없이 끝냈다", redesign)
        self.assertIn("관찰법", motion)
        self.assertIn("ID 계약", review)
        self.assertIn("독립 검수(별도 맥락)", review)
        self.assertIn("재열람 기반 자체 검수", review)
        self.assertIn("선택 게이트 미통과", budget)

    def test_readme_mentions_run_budget_and_eval_set(self) -> None:
        text = read_doc("README.md")
        for term in ("RUN-BUDGET.md", "evals/README.md", "스케치", "실행량"):
            with self.subTest(term=term):
                self.assertTrue(term in text, f"README.md must contain {term!r}")


if __name__ == "__main__":
    unittest.main()
