#!/usr/bin/env python3
"""gx-design 평가 러너 — Codex CLI 비대화 실행으로 시나리오를 돌리고 실행량을 기록한다.

표준 라이브러리만 사용한다. 실제 codex 호출 없이 명령만 보려면 --dry-run.

흐름(시나리오 1개 × 모드 1개):
  1. 새 작업 폴더를 만들고 시나리오 fixtures를 복사한다.
  2. `codex exec --json ... -` 로 첫 요청을 보낸다(프롬프트는 stdin).
  3. 평가 전용 sidecar의 현재 결정과 일치하는 checkpoint만 resume으로 보낸다.
  4. 명시적 완료, 대기, 예상 밖 질문 또는 max_turns에서 멈춘다.
  5. 토큰 사용량·도구 호출 수·턴별 마지막 메시지·생성 파일을
     results/<timestamp>/<scenario>-<mode>.json 에 저장한다.

이벤트 스키마는 Codex 버전마다 다를 수 있으므로 파서는 관대하게 동작하고,
원본 이벤트는 같은 폴더의 .events.jsonl 에 그대로 남긴다.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Iterable

EVALS_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVALS_DIR.parent
SCENARIO_DIR = EVALS_DIR / "scenarios"
RESULTS_DIR = EVALS_DIR / "results"

MODES = ("core", "full")
MODE_LABELS = {"core": "핵심 모드", "full": "전체 모드"}
SKILLS = ("gx-design", "gx-redesign")
REQUIRED_KEYS = ("id", "skill", "request", "mode", "answers", "max_turns", "expected")
STATE_FILE = ".gx-eval-state.json"
PROTOCOL = "gx-eval-dialogue/v1"
DECISION_KEYS = ("id", "type", "scope_version")
RESPONSE_STATUSES = {"answered", "delegated", "partial", "empty", "cancelled",
                     "rejected", "status_query", "stopped", "scope_change"}
OBSERVATION_LIMITS = (
    "Content SHA-256 snapshots cover turn boundaries in the workdir. Available file_change "
    "and command events are retained, including in-turn/reverted changes. Arbitrary shell "
    "writes/restores, external paths, missing events and remote tools can be invisible. "
    "A clean diff plus assistant assertions does not prove absence of unauthorized mutation. "
    "The evaluator sidecar is a dialogue signal, not independent artifact verification."
)

# 세션/스레드 시작 이벤트로 보는 type 값(소문자 비교, 부분 일치 허용).
_SESSION_EVENT_HINTS = ("thread.started",)
# 도구 호출로 세지 않는 아이템 type.
_NON_TOOL_ITEM_TYPES = {"agent_message", "assistant_message", "message", "reasoning",
                        "user_message", "error", "todo_list"}
_TOOL_HINTS = ("command", "exec", "tool", "mcp", "patch", "file_change", "web_search", "search")


class ScenarioError(ValueError):
    """시나리오 파일이 규격에 맞지 않을 때."""


# ---------------------------------------------------------------- 시나리오

def validate_scenario(data: Any, source: str = "<scenario>") -> dict:
    if not isinstance(data, dict):
        raise ScenarioError(f"{source}: 최상위는 객체여야 한다")
    missing = [key for key in REQUIRED_KEYS if key not in data and not (key == "answers" and "dialogue" in data)]
    if missing:
        raise ScenarioError(f"{source}: 필수 키 누락 {missing}")
    if not isinstance(data["id"], str) or not data["id"].strip():
        raise ScenarioError(f"{source}: id는 비어 있지 않은 문자열")
    if data["skill"] not in SKILLS:
        raise ScenarioError(f"{source}: skill은 {SKILLS} 중 하나")
    if not isinstance(data["request"], str) or not data["request"].strip():
        raise ScenarioError(f"{source}: request는 비어 있지 않은 문자열")
    if data["mode"] not in MODES:
        raise ScenarioError(f"{source}: mode는 {MODES} 중 하나")
    answers = data.get("answers", [])
    if not isinstance(answers, list) or not all(isinstance(a, str) and a.strip() for a in answers):
        raise ScenarioError(f"{source}: answers는 비어 있지 않은 문자열 목록")
    max_turns = data["max_turns"]
    if isinstance(max_turns, bool) or not isinstance(max_turns, int) or max_turns < 1:
        raise ScenarioError(f"{source}: max_turns는 1 이상의 정수")
    expected = data["expected"]
    if not isinstance(expected, list) or not expected or not all(isinstance(e, str) for e in expected):
        raise ScenarioError(f"{source}: expected는 문자열 목록(1개 이상)")
    fixtures = data.get("fixtures", [])
    if not isinstance(fixtures, list):
        raise ScenarioError(f"{source}: fixtures는 목록")
    for fixture in fixtures:
        if not (isinstance(fixture, dict) and isinstance(fixture.get("src"), str)):
            raise ScenarioError(f"{source}: fixture는 {{src, dest?}} 객체")
    if "dialogue" in data:
        dialogue = data["dialogue"]
        if not isinstance(dialogue, dict) or type(dialogue.get("version")) is not int or dialogue["version"] != 1:
            raise ScenarioError(f"{source}: dialogue.version must be 1")
        if not isinstance(dialogue.get("checkpoints"), list):
            raise ScenarioError(f"{source}: dialogue.checkpoints must be a list")
        for checkpoint in dialogue["checkpoints"]:
            if not isinstance(checkpoint, dict):
                raise ScenarioError(f"{source}: checkpoint must be an object")
            decision_key(checkpoint.get("decision"))
            response = checkpoint.get("response")
            if (not isinstance(response, dict) or not isinstance(response.get("status"), str)
                    or response["status"] not in RESPONSE_STATUSES):
                raise ScenarioError(f"{source}: invalid checkpoint response status")
            value = response.get("value")
            if value is not None and not isinstance(value, str):
                raise ScenarioError(f"{source}: response.value must be string or null")
            if response["status"] in {"answered", "delegated", "scope_change"} and (not value or not value.strip()):
                raise ScenarioError(f"{source}: affirmative responses require explicit value")
            invalidates = response.get("invalidates", [])
            if not isinstance(invalidates, list):
                raise ScenarioError(f"{source}: response.invalidates must be a list")
            if invalidates and response["status"] != "scope_change":
                raise ScenarioError(f"{source}: only explicit scope_change may invalidate decisions")
            if response["status"] == "scope_change" and not invalidates:
                raise ScenarioError(f"{source}: scope_change requires explicit invalidates")
            identities = []
            for invalidated in invalidates:
                identities.append(decision_key(invalidated))
                if not isinstance(invalidated.get("reason"), str) or not invalidated["reason"].strip():
                    raise ScenarioError(f"{source}: invalidation requires explicit reason")
            if len(identities) != len(set(identities)):
                raise ScenarioError(f"{source}: duplicate invalidation identity")
    normalized = dict(data)
    normalized.setdefault("answers", [])
    normalized.setdefault("fixtures", [])
    normalized.setdefault("title", data["id"])
    return normalized


def load_scenario(path: Path) -> dict:
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ScenarioError(f"{path.name}: JSON 파싱 실패 — {exc}") from exc
    return validate_scenario(data, path.name)


def load_scenarios(directory: Path = SCENARIO_DIR, only: Iterable[str] | None = None) -> list[dict]:
    wanted = set(only or ())
    scenarios = []
    for path in sorted(Path(directory).glob("*.json")):
        scenario = load_scenario(path)
        if wanted and scenario["id"] not in wanted and path.stem not in wanted:
            continue
        scenarios.append(scenario)
    return scenarios


def build_initial_prompt(scenario: dict, mode: str) -> str:
    return f"${scenario['skill']} {scenario['request']}\n\n진행 모드: {MODE_LABELS[mode]}"


def decision_key(decision: Any) -> tuple[str, str, str]:
    if not isinstance(decision, dict) or any(
            not isinstance(decision.get(key), str) or not decision[key].strip() for key in DECISION_KEYS):
        raise ScenarioError("decision requires nonempty id/type/scope_version")
    return tuple(decision[key] for key in DECISION_KEYS)


def protocol_prompt(prompt: str, nonce: str, scenario: dict) -> str:
    # Test instrumentation only: never add this protocol to product-user flows.
    identities = [cp["decision"] for cp in scenario.get("dialogue", {}).get("checkpoints", [])]
    return (prompt + f"\n\n[Evaluator instrumentation, not user approval]\nGX_EVAL_NONCE={nonce}\n"
            f"Before ending this turn write {STATE_FILE} as JSON: "
            f'{{"protocol":"{PROTOCOL}","nonce":"{nonce}","state":"waiting|completed|stopped|unverified",'
            '"pending":[{"id":"...","type":"...","scope_version":"...",'
            '"required":true,"status":"unresolved|partial"}]}. '
            "Report actual state; do not invent a question to obtain a prepared answer. "
            "completed requires no unresolved required decisions; unverified means required evidence unavailable. "
            "A required decision remains outstanding until its explicit answered/delegated reply. "
            "Only a scripted scope_change reply's invalidates entries authorize withdrawal. "
            "Confirm withdrawal in invalidated:[{id,type,scope_version,reason}], copying that exact identity and reason. "
            "Model-authored reasons alone never authorize withdrawal. "
            "Use these identity labels only if their decisions actually apply: " + json.dumps(identities, ensure_ascii=False) +
            ". Replies carry decision and response status; empty/cancelled/partial/status_query are not approval. "
            "Never infer approval from absence of a reply. This sidecar does not verify artifacts.")


def read_dialogue_signal(workdir: Path, nonce: str) -> tuple[dict | None, str | None]:
    path = workdir / STATE_FILE
    if not path.exists():
        return None, "missing_signal"
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(state, dict) or state.get("protocol") != PROTOCOL or state.get("nonce") != nonce:
            return None, "stale_or_invalid_signal"
        if not isinstance(state.get("state"), str) or state["state"] not in {"waiting", "completed", "stopped", "unverified"}:
            return None, "invalid_signal"
        pending = state.get("pending")
        if not isinstance(pending, list):
            return None, "invalid_signal"
        keys = []
        for item in pending:
            keys.append(decision_key(item))
            if (not isinstance(item.get("required"), bool) or not isinstance(item.get("status"), str)
                    or item["status"] not in {"unresolved", "partial"}):
                return None, "invalid_signal"
        if len(keys) != len(set(keys)) or (state["state"] == "completed" and any(p["required"] for p in pending)):
            return None, "invalid_signal"
        if state["state"] == "waiting" and not pending:
            return None, "invalid_signal"
        invalidated = state.get("invalidated", [])
        if not isinstance(invalidated, list):
            return None, "invalid_signal"
        for item in invalidated:
            decision_key(item)
            if not isinstance(item.get("reason"), str) or not item["reason"].strip():
                return None, "invalid_signal"
        return state, None
    except (ValueError, OSError):
        return None, "invalid_signal"


def next_checkpoint(scenario: dict, state: dict, cursor: int) -> tuple[dict | None, str]:
    if state["state"] != "waiting":
        return None, state["state"]
    if "dialogue" not in scenario:
        return None, "legacy_unbound_answers"
    checkpoints = scenario["dialogue"]["checkpoints"]
    if cursor >= len(checkpoints):
        return None, "waiting"
    checkpoint = checkpoints[cursor]
    if decision_key(checkpoint["decision"]) not in {decision_key(p) for p in state["pending"]}:
        return None, "unexpected_question"
    return checkpoint, "resume"


# ---------------------------------------------------------------- 명령

def build_start_command(codex_bin: str, workdir: Path, sandbox: str,
                        last_message_file: Path | None = None) -> list[str]:
    cmd = [codex_bin, "exec", "--json", "--skip-git-repo-check", "-s", sandbox, "-C", str(workdir)]
    if last_message_file is not None:
        cmd += ["-o", str(last_message_file)]
    cmd.append("-")  # 프롬프트는 stdin (Windows 셸 인용·한글 깨짐 회피)
    return cmd


def build_resume_command(codex_bin: str, session_id: str, sandbox: str,
                         last_message_file: Path | None = None) -> list[str]:
    cmd = [codex_bin, "exec", "resume", "--json", "--skip-git-repo-check",
           "-c", f"sandbox_mode={sandbox}"]
    if last_message_file is not None:
        cmd += ["-o", str(last_message_file)]
    cmd += [session_id, "-"]
    return cmd


# ---------------------------------------------------------------- 이벤트 파싱

def parse_jsonl(text: str) -> tuple[list[dict], list[str]]:
    """JSONL 텍스트 → (이벤트 목록, JSON이 아닌 줄 목록)."""
    events, junk = [], []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            junk.append(line)
            continue
        if isinstance(value, dict):
            events.append(value)
        else:
            junk.append(line)
    return events, junk


def event_type(event: dict) -> str:
    value = event.get("type")
    if not isinstance(value, str):
        msg = event.get("msg")
        if isinstance(msg, dict) and isinstance(msg.get("type"), str):
            value = msg["type"]
    return value if isinstance(value, str) else "unknown"


def extract_session_id(events: Iterable[dict]) -> str | None:
    """문서화된 thread.started 이벤트의 thread_id만 세션 ID로 사용한다."""
    for event in events:
        if event_type(event) == "thread.started":
            value = event.get("thread_id")
            if isinstance(value, str) and value:
                return value
    return None


def _iter_usage_objects(node: Any):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "usage" and isinstance(value, dict):
                yield value
            else:
                yield from _iter_usage_objects(value)
    elif isinstance(node, list):
        for value in node:
            yield from _iter_usage_objects(value)


def sum_usage(events: Iterable[dict]) -> dict:
    """모든 `usage` 객체의 숫자 키를 합산한다(키 이름 고정 없음)."""
    totals: dict[str, int | float] = {}
    for event in events:
        for usage in _iter_usage_objects(event):
            for key, value in usage.items():
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    continue
                totals[key] = totals.get(key, 0) + value
    return totals


def last_cumulative_usage(events: Iterable[dict]) -> dict:
    """구형 이벤트(token_count.info.total_token_usage)는 누적값이므로 마지막 것만 쓴다."""
    found: dict = {}

    def walk(node: Any) -> None:
        nonlocal found
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "total_token_usage" and isinstance(value, dict):
                    found = {k: v for k, v in value.items()
                             if isinstance(v, (int, float)) and not isinstance(v, bool)}
                else:
                    walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    for event in events:
        walk(event)
    return found


def _item_of(event: dict) -> dict | None:
    item = event.get("item")
    if isinstance(item, dict):
        return item
    msg = event.get("msg")
    if isinstance(msg, dict):
        return msg
    return None


def count_tools(events: Iterable[dict]) -> dict:
    """도구·명령 호출을 종류별로 센다.

    item.* 형식: 같은 아이템의 started/completed 중복을 피하려고 완료 이벤트만(없으면 시작) 센다.
    그 외 형식: type 이름에 도구 힌트가 있고 begin/start/completed/end 접미가 있는 이벤트를 센다.
    """
    counts: dict[str, int] = {}
    seen_ids: set[str] = set()
    pending: dict[str, str] = {}
    for event in events:
        etype = event_type(event)
        item = event.get("item") if isinstance(event.get("item"), dict) else None
        if item is not None:
            itype = item.get("type") or item.get("item_type") or "unknown"
            if not isinstance(itype, str) or itype in _NON_TOOL_ITEM_TYPES:
                continue
            item_id = item.get("id") if isinstance(item.get("id"), str) else None
            if etype.endswith("completed"):
                if item_id and item_id in seen_ids:
                    continue
                if item_id:
                    seen_ids.add(item_id)
                    pending.pop(item_id, None)
                counts[itype] = counts.get(itype, 0) + 1
            elif item_id and item_id not in seen_ids:
                pending[item_id] = itype
            continue
        lowered = etype.lower()
        if any(h in lowered for h in _TOOL_HINTS) and lowered.endswith(("_begin", ".started", "_start")):
            counts[etype] = counts.get(etype, 0) + 1
    for itype in pending.values():  # 완료 이벤트 없이 끝난 아이템
        counts[itype] = counts.get(itype, 0) + 1
    return counts


def agent_messages(events: Iterable[dict]) -> list[str]:
    texts = []
    for event in events:
        item = _item_of(event)
        if not item:
            continue
        itype = item.get("type") or item.get("item_type")
        if itype in ("agent_message", "assistant_message"):
            text = item.get("text") or item.get("message")
            if isinstance(text, str) and text.strip():
                if event_type(event).endswith("started"):
                    continue
                texts.append(text)
    return texts


def summarize_events(events: list[dict]) -> dict:
    types: dict[str, int] = {}
    for event in events:
        etype = event_type(event)
        types[etype] = types.get(etype, 0) + 1
    messages = agent_messages(events)
    usage = turn_completed_usage(events) or sum_usage(events) or last_cumulative_usage(events)
    return {
        "session_id": extract_session_id(events),
        "usage": usage,
        "tool_counts": count_tools(events),
        "event_types": types,
        "last_message": messages[-1] if messages else None,
    }


def turn_completed_usage(events: Iterable[dict]) -> dict:
    """turn.completed usage의 마지막 값을 추출한다(세션 누적값)."""
    found = {}
    for event in events:
        if event_type(event) == "turn.completed" and isinstance(event.get("usage"), dict):
            found = {k: v for k, v in event["usage"].items()
                     if isinstance(v, (int, float)) and not isinstance(v, bool)}
    return found


def aggregate_turn_usage(usages: list[dict]) -> tuple[list[dict], dict, str]:
    """턴 usage를 누적 또는 합산으로 판정하고 턴별 delta와 최종값을 돌려준다."""
    cumulative = all(
        all(value >= previous[key] for key, value in current.items() if key in previous)
        for previous, current in zip(usages, usages[1:])
    )
    mode = "cumulative" if cumulative else "summed"
    deltas, previous = [], {}
    for usage in usages:
        delta = {}
        for key, value in usage.items():
            delta[key] = value - previous.get(key, 0) if cumulative else value
        deltas.append(delta)
        previous = usage
    total = dict(usages[-1]) if usages and cumulative else {}
    if usages and not cumulative:
        for usage in usages:
            merge_counts(total, usage)
    uncached = max(0, total.get("input_tokens", 0) - total.get("cached_input_tokens", 0))
    total["uncached_input_tokens"] = uncached
    return deltas, total, mode


def merge_counts(target: dict, extra: dict) -> dict:
    for key, value in extra.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        target[key] = target.get(key, 0) + value
    return target


# ---------------------------------------------------------------- 작업 폴더

def snapshot(directory: Path) -> dict[str, tuple[int, str]]:
    """Keep the old mapping/two-tuple API; second field is now content SHA-256, not mtime."""
    state = {}
    for path in Path(directory).rglob("*"):
        if path.is_file() and path.relative_to(directory).as_posix() != STATE_FILE:
            digest = hashlib.sha256()
            size = 0
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    size += len(chunk)
                    digest.update(chunk)
            state[path.relative_to(directory).as_posix()] = (size, digest.hexdigest())
    return state


def changed_files(before: dict, after: dict) -> dict:
    return {
        "created": sorted(p for p in after if p not in before),
        "modified": sorted(p for p in after if p in before and after[p] != before[p]),
        "deleted": sorted(p for p in before if p not in after),
    }


def prepare_workdir(scenario: dict, workdir: Path) -> list[str]:
    if workdir.exists():
        if not workdir.is_dir() or any(workdir.iterdir()):
            raise ScenarioError(f"작업 폴더가 이미 있고 비어 있지 않음: {workdir}")
    else:
        workdir.mkdir(parents=True)
    copied = []
    for fixture in scenario.get("fixtures", []):
        src = (REPO_ROOT / fixture["src"]).resolve()
        dest = workdir / fixture.get("dest", Path(fixture["src"]).name)
        if not src.exists():
            raise ScenarioError(f"{scenario['id']}: fixture 없음 {fixture['src']}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dest)
        copied.append(dest.relative_to(workdir).as_posix())
    return copied


def validate_workdir(workdir: Path, results_dir: Path, repo_root: Path = REPO_ROOT) -> None:
    """작업 폴더의 Git 경계와 저장소 덮어쓰기 위험을 검사한다."""
    workdir, results_dir, repo_root = (Path(p).resolve() for p in (workdir, results_dir, repo_root))
    # The default disposable run copies live here; allow this dedicated subtree only.
    if results_dir == repo_root / "evals" / "results" and results_dir in workdir.parents:
        return
    if workdir == repo_root or repo_root in workdir.parents or workdir in repo_root.parents:
        raise ScenarioError(f"작업 폴더가 저장소 루트와 겹치거나 저장소 안에 있음: {workdir}")
    if workdir == results_dir or results_dir in workdir.parents or workdir in results_dir.parents:
        return
    for parent in (workdir, *workdir.parents):
        if (parent / ".git").exists():
            raise ScenarioError(f"작업 폴더가 Git 작업 트리 안에 있음: {workdir}")


# ---------------------------------------------------------------- 실행

def _run_turn(cmd: list[str], prompt: str, env: dict, cwd: Path, timeout: int) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, input=prompt.encode("utf-8"), stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, env=env, cwd=str(cwd), timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or b"").decode("utf-8", "replace")
        err = (exc.stderr or b"").decode("utf-8", "replace")
        return -1, out, err + f"\n[timeout after {timeout}s]"
    return (proc.returncode, proc.stdout.decode("utf-8", "replace"),
            proc.stderr.decode("utf-8", "replace"))


def run_scenario(scenario: dict, mode: str, args: argparse.Namespace, run_dir: Path) -> dict:
    scenario = validate_scenario(scenario)
    name = f"{scenario['id']}-{mode}"
    base = Path(args.workdir).resolve() if args.workdir else run_dir / "work"
    workdir = base / name
    max_turns = min(scenario["max_turns"], args.max_turns) if args.max_turns else scenario["max_turns"]
    prompt = build_initial_prompt(scenario, mode)
    checkpoints = scenario.get("dialogue", {}).get("checkpoints", [])

    env = os.environ.copy()
    if args.codex_home:
        env["CODEX_HOME"] = str(Path(args.codex_home).resolve())

    if args.dry_run:
        print(f"# {name}  (workdir: {workdir}, turns ≤ {max_turns})")
        if args.codex_home:
            print(f"#   CODEX_HOME={env['CODEX_HOME']}")
        cmd = build_start_command(args.codex_bin, workdir, args.sandbox, run_dir / f"{name}.turn1.last.md")
        print("  $ " + " ".join(cmd))
        print("    stdin: " + prompt.replace("\n", " / "))
        print(f"    evaluator protocol: {PROTOCOL}; fresh nonce required each turn")
        if "dialogue" not in scenario:
            print(f"    LEGACY: {len(scenario.get('answers', []))} unbound answers retained but never auto-sent; add dialogue checkpoints")
        for checkpoint in checkpoints:
            print("    conditional checkpoint: " + json.dumps(checkpoint, ensure_ascii=False))
        return {}

    run_started = time.perf_counter()
    run_dir.mkdir(parents=True, exist_ok=True)
    validate_workdir(workdir, Path(args.results_dir))
    fixtures = prepare_workdir(scenario, workdir)
    before = snapshot(workdir)
    raw_log = run_dir / f"{name}.events.jsonl"
    turns, per_turn_usages, tools = [], [], {}
    session_id, stop_reason = None, "max_turns"
    cursor = 0
    outstanding_required = set()
    authorized_invalidations = {}

    with raw_log.open("w", encoding="utf-8") as log:
        for index in range(1, max_turns + 1):
            nonce = uuid.uuid4().hex
            turn_prompt = protocol_prompt(prompt, nonce, scenario)
            last_file = run_dir / f"{name}.turn{index}.last.md"
            if index == 1:
                cmd = build_start_command(args.codex_bin, workdir, args.sandbox, last_file)
            else:
                cmd = build_resume_command(args.codex_bin, session_id, args.sandbox, last_file)
            turn_before = snapshot(workdir)
            turn_started = time.perf_counter()
            code, out, err = _run_turn(cmd, turn_prompt, env, workdir, args.timeout)
            turn_elapsed = time.perf_counter() - turn_started
            turn_after = snapshot(workdir)
            turn_files = changed_files(turn_before, turn_after)
            dialogue_state, signal_error = read_dialogue_signal(workdir, nonce)
            log.write(json.dumps({"_runner": "turn", "turn": index, "returncode": code}, ensure_ascii=False) + "\n")
            log.write(out if out.endswith("\n") or not out else out + "\n")
            events, junk = parse_jsonl(out)
            summary = summarize_events(events)
            reported_id = summary["session_id"]
            if index == 1:
                session_id = reported_id
            elif reported_id is not None and reported_id != session_id:
                stop_reason = "session_mismatch"
            per_turn_usages.append(summary["usage"])
            merge_counts(tools, summary["tool_counts"])
            last_message = (last_file.read_text(encoding="utf-8", errors="replace")
                            if last_file.exists() else summary["last_message"])
            turns.append({
                "turn": index,
                "prompt": turn_prompt,
                "returncode": code,
                "elapsed_seconds": turn_elapsed,
                "usage": summary["usage"],
                "usage_cumulative": summary["usage"],
                "tool_counts": summary["tool_counts"],
                "event_types": summary["event_types"],
                "files": turn_files,  # 이 턴에서 생성·수정·삭제된 파일(게이트 준수 판정용)
                "file_hashes_before": turn_before,
                "file_hashes_after": turn_after,
                "mutation_events": [event for event in events if any(
                    hint in str((_item_of(event) or {}).get("type", event_type(event))).lower()
                    for hint in ("file_change", "command", "exec", "patch"))],
                "dialogue_signal": dialogue_state,
                "signal_error": signal_error,
                "non_json_lines": len(junk),
                "stderr_tail": err[-2000:],
                "last_message": last_message,
            })
            if index > 1 and stop_reason == "session_mismatch":
                break
            if code != 0:
                stop_reason = f"error_turn_{index}"
                break
            if session_id is None:
                stop_reason = "no_session_id"
                break
            if signal_error:
                stop_reason = signal_error
                break
            invalidated_decisions = dialogue_state.get("invalidated", [])
            if any(authorized_invalidations.get(decision_key(item)) != item["reason"]
                   for item in invalidated_decisions):
                stop_reason = "unauthorized_invalidation"
                break
            for invalidated in invalidated_decisions:
                outstanding_required.discard(decision_key(invalidated))
                authorized_invalidations.pop(decision_key(invalidated), None)
            outstanding_required.update(decision_key(p) for p in dialogue_state["pending"] if p["required"])
            if dialogue_state["state"] == "completed" and outstanding_required:
                stop_reason = "unresolved_required"
                break
            checkpoint, stop_reason = next_checkpoint(scenario, dialogue_state, cursor)
            if checkpoint is None:
                break
            if index == max_turns:
                stop_reason = "max_turns"
                break
            # Only an exact, current pending decision authorizes this test response.
            prompt = "[Evaluator reply]\n" + json.dumps(checkpoint, ensure_ascii=False)
            turns[-1]["dispatched_checkpoint"] = checkpoint
            if checkpoint["response"]["status"] in {"answered", "delegated"}:
                outstanding_required.discard(decision_key(checkpoint["decision"]))
            if checkpoint["response"]["status"] == "scope_change":
                for invalidated in checkpoint["response"]["invalidates"]:
                    authorized_invalidations[decision_key(invalidated)] = invalidated["reason"]
            cursor += 1

    usage_deltas, usage, usage_mode = aggregate_turn_usage(per_turn_usages)
    for turn, delta in zip(turns, usage_deltas):
        turn["usage_delta"] = delta
    after = snapshot(workdir)
    files = changed_files(before, after)
    result = {
        "scenario": scenario["id"],
        "title": scenario.get("title"),
        "skill": scenario["skill"],
        "mode": mode,
        "session_id": session_id,
        "stop_reason": stop_reason,
        "elapsed_seconds": time.perf_counter() - run_started,
        "turn_elapsed_seconds": sum(turn["elapsed_seconds"] for turn in turns),
        "timing_scope": "Monotonic active scripted runner through result assembly; turn durations cover CLI calls. Excludes human reply waiting and final result write/print; not evidence of speedup.",
        "eligible_for_success_average": stop_reason == "completed",
        "dialogue_format": "state-aware-v1" if "dialogue" in scenario else "legacy-unbound",
        "checkpoints_dispatched": cursor,
        "outstanding_required": [dict(zip(DECISION_KEYS, key)) for key in sorted(outstanding_required)],
        "unused_checkpoints": checkpoints[cursor:],
        "legacy_answers_not_dispatched": scenario.get("answers", []),
        "observation_limits": OBSERVATION_LIMITS,
        "snapshot_format": "path -> [size_bytes, sha256] (v2; formerly size/mtime)",
        "turn_count": len(turns),
        "usage": usage,
        "uncached_input_tokens": usage.get("uncached_input_tokens", 0),
        "usage_mode": usage_mode,
        "tool_counts": tools,
        "tool_calls": sum(tools.values()),
        "turns": turns,
        "workdir": str(workdir),
        "fixtures": fixtures,
        "files": files,
        "file_hashes_before": before,
        "file_hashes_after": after,
        "expected": scenario["expected"],
        "sandbox": args.sandbox,
        "codex_home": env.get("CODEX_HOME") if args.codex_home else None,
        "raw_events": raw_log.name,
    }
    out_path = run_dir / f"{name}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[{name}] turns={len(turns)} stop={stop_reason} tool_calls={result['tool_calls']} "
          f"usage={usage} -> {out_path}")
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="gx-design 평가 러너 (codex exec)")
    parser.add_argument("--scenario", action="append", default=[],
                        help="시나리오 id 또는 파일 이름(확장자 제외). 반복 가능. 생략 시 전체")
    parser.add_argument("--scenario-dir", type=Path, default=SCENARIO_DIR,
                        help="시나리오 폴더; 새 계약은 evals/dialogue-scenarios")
    parser.add_argument("--mode", choices=MODES + ("scenario", "both"), default="scenario",
                        help="core|full|both, 기본은 시나리오 파일의 mode")
    parser.add_argument("--codex-home", help="격리 CODEX_HOME 경로(하위 프로세스 환경에만 설정)")
    parser.add_argument("--workdir", help="실행별 작업 폴더의 상위 경로(기본: results/<timestamp>/work)")
    parser.add_argument("--results-dir", default=str(RESULTS_DIR), help="결과 루트(기본 evals/results)")
    parser.add_argument("--sandbox", default="workspace-write",
                        choices=("read-only", "workspace-write", "danger-full-access"))
    parser.add_argument("--max-turns", type=int, default=0, help="시나리오 max_turns보다 작으면 이 값으로 제한")
    parser.add_argument("--timeout", type=int, default=1800, help="턴당 제한 시간(초)")
    parser.add_argument("--codex-bin", default=None, help="codex 실행 파일(기본: PATH에서 탐색)")
    parser.add_argument("--dry-run", action="store_true", help="명령만 출력하고 실행하지 않는다")
    args = parser.parse_args(argv)
    if args.codex_bin is None:
        args.codex_bin = shutil.which("codex") or "codex"
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    scenarios = load_scenarios(args.scenario_dir, args.scenario)
    if not scenarios:
        print("선택된 시나리오가 없다", file=sys.stderr)
        return 2
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = Path(args.results_dir).resolve() / stamp
    if run_dir.exists() and any(run_dir.iterdir()):
        raise ScenarioError(f"결과 폴더가 이미 있고 비어 있지 않음: {run_dir}")
    for scenario in scenarios:
        if args.mode == "scenario":
            modes = [scenario["mode"]]
        elif args.mode == "both":
            modes = list(MODES)
        else:
            modes = [args.mode]
        for mode in modes:
            run_scenario(scenario, mode, args, run_dir)
    if not args.dry_run:
        print(f"결과: {run_dir}\n집계: python evals/score.py {run_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
