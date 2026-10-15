#!/usr/bin/env python3
"""gx-design 평가 러너 — Codex CLI 비대화 실행으로 시나리오를 돌리고 실행량을 기록한다.

표준 라이브러리만 사용한다. 실제 codex 호출 없이 명령만 보려면 --dry-run.

흐름(시나리오 1개 × 모드 1개):
  1. 새 작업 폴더를 만들고 시나리오 fixtures를 복사한다.
  2. `codex exec --json ... -` 로 첫 요청을 보낸다(프롬프트는 stdin).
  3. JSONL 이벤트에서 세션 ID를 찾고, answers를 순서대로
     `codex exec resume --json ... <SESSION_ID> -` 로 넣는다.
  4. answers 소진 또는 max_turns 도달 시 멈춘다.
  5. 토큰 사용량·도구 호출 수·턴별 마지막 메시지·생성 파일을
     results/<timestamp>/<scenario>-<mode>.json 에 저장한다.

이벤트 스키마는 Codex 버전마다 다를 수 있으므로 파서는 관대하게 동작하고,
원본 이벤트는 같은 폴더의 .events.jsonl 에 그대로 남긴다.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import subprocess
import sys
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

# 세션/스레드 시작 이벤트로 보는 type 값(소문자 비교, 부분 일치 허용).
_SESSION_EVENT_HINTS = ("thread.started", "thread_started", "session.created",
                        "session_configured", "session.started", "session_started")
_SESSION_ID_KEYS = ("thread_id", "session_id", "conversation_id")
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
    missing = [key for key in REQUIRED_KEYS if key not in data]
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
    answers = data["answers"]
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
    normalized = dict(data)
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
    """세션/스레드 시작 이벤트에서 ID를 찾는다. 없으면 아무 이벤트의 thread_id/session_id."""
    fallback = None
    for event in events:
        etype = event_type(event).lower()
        containers = [event]
        for key in ("msg", "thread", "session", "payload", "data"):
            if isinstance(event.get(key), dict):
                containers.append(event[key])
        is_start = any(hint in etype for hint in _SESSION_EVENT_HINTS)
        for container in containers:
            for key in _SESSION_ID_KEYS:
                value = container.get(key)
                if isinstance(value, str) and value:
                    if is_start:
                        return value
                    fallback = fallback or value
            if is_start and container is not event and isinstance(container.get("id"), str):
                return container["id"]
        if is_start and isinstance(event.get("id"), str) and event["id"]:
            return event["id"]
    return fallback


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
    usage = sum_usage(events) or last_cumulative_usage(events)
    return {
        "session_id": extract_session_id(events),
        "usage": usage,
        "tool_counts": count_tools(events),
        "event_types": types,
        "last_message": messages[-1] if messages else None,
    }


def merge_counts(target: dict, extra: dict) -> dict:
    for key, value in extra.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        target[key] = target.get(key, 0) + value
    return target


# ---------------------------------------------------------------- 작업 폴더

def snapshot(directory: Path) -> dict[str, tuple[int, int]]:
    state = {}
    for path in Path(directory).rglob("*"):
        if path.is_file():
            stat = path.stat()
            state[path.relative_to(directory).as_posix()] = (stat.st_size, stat.st_mtime_ns)
    return state


def changed_files(before: dict, after: dict) -> dict:
    return {
        "created": sorted(p for p in after if p not in before),
        "modified": sorted(p for p in after if p in before and after[p] != before[p]),
        "deleted": sorted(p for p in before if p not in after),
    }


def prepare_workdir(scenario: dict, workdir: Path) -> list[str]:
    workdir.mkdir(parents=True, exist_ok=True)
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
    name = f"{scenario['id']}-{mode}"
    base = Path(args.workdir).resolve() if args.workdir else run_dir / "work"
    workdir = base / name
    max_turns = min(scenario["max_turns"], args.max_turns) if args.max_turns else scenario["max_turns"]
    prompts = [build_initial_prompt(scenario, mode)] + list(scenario["answers"])
    prompts = prompts[:max_turns]

    env = os.environ.copy()
    if args.codex_home:
        env["CODEX_HOME"] = str(Path(args.codex_home).resolve())

    if args.dry_run:
        print(f"# {name}  (workdir: {workdir}, turns ≤ {len(prompts)})")
        if args.codex_home:
            print(f"#   CODEX_HOME={env['CODEX_HOME']}")
        for index, prompt in enumerate(prompts, 1):
            cmd = (build_start_command(args.codex_bin, workdir, args.sandbox, run_dir / f"{name}.turn{index}.last.md")
                   if index == 1 else
                   build_resume_command(args.codex_bin, "<SESSION_ID>", args.sandbox,
                                        run_dir / f"{name}.turn{index}.last.md"))
            print("  $ " + " ".join(cmd))
            print("    stdin: " + prompt.replace("\n", " / "))
        return {}

    run_dir.mkdir(parents=True, exist_ok=True)
    fixtures = prepare_workdir(scenario, workdir)
    before = snapshot(workdir)
    raw_log = run_dir / f"{name}.events.jsonl"
    turns, usage, tools = [], {}, {}
    session_id, stop_reason = None, "answers_exhausted"

    with raw_log.open("w", encoding="utf-8") as log:
        for index, prompt in enumerate(prompts, 1):
            last_file = run_dir / f"{name}.turn{index}.last.md"
            if index == 1:
                cmd = build_start_command(args.codex_bin, workdir, args.sandbox, last_file)
            else:
                cmd = build_resume_command(args.codex_bin, session_id, args.sandbox, last_file)
            turn_before = snapshot(workdir)
            code, out, err = _run_turn(cmd, prompt, env, workdir, args.timeout)
            turn_files = changed_files(turn_before, snapshot(workdir))
            log.write(json.dumps({"_runner": "turn", "turn": index, "returncode": code}, ensure_ascii=False) + "\n")
            log.write(out if out.endswith("\n") or not out else out + "\n")
            events, junk = parse_jsonl(out)
            summary = summarize_events(events)
            session_id = session_id or summary["session_id"]
            merge_counts(usage, summary["usage"])
            merge_counts(tools, summary["tool_counts"])
            last_message = (last_file.read_text(encoding="utf-8", errors="replace")
                            if last_file.exists() else summary["last_message"])
            turns.append({
                "turn": index,
                "prompt": prompt,
                "returncode": code,
                "usage": summary["usage"],
                "tool_counts": summary["tool_counts"],
                "event_types": summary["event_types"],
                "files": turn_files,  # 이 턴에서 생성·수정·삭제된 파일(게이트 준수 판정용)
                "non_json_lines": len(junk),
                "stderr_tail": err[-2000:],
                "last_message": last_message,
            })
            if code != 0:
                stop_reason = f"error_turn_{index}"
                break
            if session_id is None:
                stop_reason = "no_session_id"
                break
        else:
            if len(prompts) < 1 + len(scenario["answers"]):
                stop_reason = "max_turns"

    files = changed_files(before, snapshot(workdir))
    result = {
        "scenario": scenario["id"],
        "title": scenario.get("title"),
        "skill": scenario["skill"],
        "mode": mode,
        "session_id": session_id,
        "stop_reason": stop_reason,
        "turn_count": len(turns),
        "usage": usage,
        "tool_counts": tools,
        "tool_calls": sum(tools.values()),
        "turns": turns,
        "workdir": str(workdir),
        "fixtures": fixtures,
        "files": files,
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
    scenarios = load_scenarios(SCENARIO_DIR, args.scenario)
    if not scenarios:
        print("선택된 시나리오가 없다", file=sys.stderr)
        return 2
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = Path(args.results_dir).resolve() / stamp
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
