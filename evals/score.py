#!/usr/bin/env python3
"""평가 결과 집계 — run_eval.py 결과 JSON을 모아 시나리오×모드 표(마크다운)로 출력한다.

    python evals/score.py evals/results/<timestamp> [다른 폴더·파일 ...] [--out table.md]

품질 점수: 결과 파일 `<scenario>-<mode>.json` 옆에 `<scenario>-<mode>.scores.json`이 있으면 합친다.
형식(rubric.md 참고):
    {"scorer": "사람 또는 에이전트 이름", "scores": {"gate_compliance": 2, ..., "motion_violations": null}}
null 은 해당 없음(N/A) — 합계와 만점에서 모두 뺀다.
표준 라이브러리만 사용한다.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

RUBRIC_KEYS = (
    "gate_compliance",
    "slop_avoidance",
    "required_sections",
    "measurable_ratio",
    "evidence_fidelity",
    "motion_violations",
)
MAX_PER_CRITERION = 2
USAGE_COLUMNS = ("input_tokens", "cached_input_tokens", "uncached_input_tokens", "output_tokens", "reasoning_output_tokens")
AVERAGE_STOP_REASONS = {"answers_exhausted", "max_turns", ""}


def _is_result_file(path: Path) -> bool:
    name = path.name
    return name.endswith(".json") and not name.endswith(".scores.json")


def collect_result_files(paths: Iterable[Path]) -> list[Path]:
    files = []
    for path in paths:
        path = Path(path)
        if path.is_dir():
            files.extend(p for p in sorted(path.rglob("*.json"))
                         if _is_result_file(p) and "work" not in p.relative_to(path).parts[:-1])
        elif path.is_file() and _is_result_file(path):
            files.append(path)
    return files


def score_path_for(result_path: Path) -> Path:
    return result_path.with_name(result_path.name[: -len(".json")] + ".scores.json")


def rubric_total(scores: dict) -> tuple[int, int]:
    """(획득 점수, 만점) — None 항목은 제외, 0~2 범위 밖은 ValueError."""
    got, maximum = 0, 0
    for key in RUBRIC_KEYS:
        value = scores.get(key)
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= MAX_PER_CRITERION:
            raise ValueError(f"rubric {key} must be 0..{MAX_PER_CRITERION} or null, got {value!r}")
        got += value
        maximum += MAX_PER_CRITERION
    return got, maximum


def load_row(result_path: Path) -> dict | None:
    try:
        data = json.loads(Path(result_path).read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None  # 작업 폴더 안의 다른 JSON 등은 건너뛴다
    if not isinstance(data, dict) or "scenario" not in data or "mode" not in data:
        return None
    usage = data.get("usage") or {}
    row = {
        "scenario": data["scenario"],
        "mode": data["mode"],
        "turns": data.get("turn_count", len(data.get("turns", []))),
        "tool_calls": data.get("tool_calls", sum((data.get("tool_counts") or {}).values())),
        "stop_reason": data.get("stop_reason", ""),
        "usage": {key: usage.get(key, 0) for key in USAGE_COLUMNS},
        "rubric": None,
        "source": str(result_path),
    }
    score_file = score_path_for(Path(result_path))
    if score_file.exists():
        try:
            score_data = json.loads(score_file.read_text(encoding="utf-8"))
            if not isinstance(score_data, dict):
                raise ValueError("최상위는 객체여야 함")
            scores = score_data.get("scores", score_data)
            if not isinstance(scores, dict):
                raise ValueError("scores는 객체여야 함")
            unknown = set(scores) - set(RUBRIC_KEYS)
            if unknown:
                raise ValueError(f"알 수 없는 기준: {sorted(unknown)}")
            got, maximum = rubric_total(scores)
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            raise ValueError(f"{score_file}: .scores.json 형식 오류: {exc}") from exc
        row["rubric"] = {"got": got, "max": maximum, "scores": scores, "scorer": score_data.get("scorer")}
    if row["stop_reason"] not in AVERAGE_STOP_REASONS:
        row["status"] = f"제외: {row['stop_reason']}"
    else:
        row["status"] = row["stop_reason"]
    return row


def aggregate(rows: Iterable[dict]) -> list[dict]:
    """같은 시나리오×모드의 여러 실행을 평균 낸다(표본 수 n 포함)."""
    groups: dict[tuple[str, str], list[dict]] = {}
    for row in rows:
        groups.setdefault((row["scenario"], row["mode"]), []).append(row)
    table = []
    for (scenario, mode), group in sorted(groups.items()):
        eligible = [r for r in group if r["stop_reason"] in AVERAGE_STOP_REASONS]
        excluded = [r for r in group if r["stop_reason"] not in AVERAGE_STOP_REASONS]
        n = len(eligible)
        rubric_rows = [r["rubric"] for r in eligible if r["rubric"]]
        entry = {
            "scenario": scenario,
            "mode": mode,
            "n": n,
            "excluded": excluded,
            "turns": sum(r["turns"] for r in eligible) / n if n else 0,
            "tool_calls": sum(r["tool_calls"] for r in eligible) / n if n else 0,
            "usage": {key: sum(r["usage"][key] for r in eligible) / n if n else 0 for key in USAGE_COLUMNS},
            "rubric": None,
        }
        if rubric_rows:
            entry["rubric"] = {
                "got": sum(r["got"] for r in rubric_rows) / len(rubric_rows),
                "max": sum(r["max"] for r in rubric_rows) / len(rubric_rows),
                "n": len(rubric_rows),
            }
        table.append(entry)
    return table


def _fmt(value: float) -> str:
    return f"{value:,.0f}" if float(value).is_integer() else f"{value:,.1f}"


def format_table(table: list[dict]) -> str:
    header = ("| 시나리오 | 모드 | 상태 | 채점 표본 수 | 턴 | 입력 토큰 | 캐시 입력 | 미캐시 입력 | 출력 토큰 | 추론 출력 | 도구 호출 | 품질(rubric) |\n"
              "|---|---|---|---|---|---|---|---|---|---|---|---|")
    lines = [header]
    for entry in table:
        usage = entry["usage"]
        rubric = entry["rubric"]
        quality = f"{_fmt(rubric['got'])}/{_fmt(rubric['max'])}" if rubric else "미채점"
        status = "평균" if entry["n"] else "평균 제외"
        lines.append(
            f"| {entry['scenario']} | {entry['mode']} | {status} | {entry['n']} | {_fmt(entry['turns'])} | "
            f"{_fmt(usage['input_tokens'])} | {_fmt(usage['cached_input_tokens'])} | "
            f"{_fmt(usage['uncached_input_tokens'])} | {_fmt(usage['output_tokens'])} | {_fmt(usage['reasoning_output_tokens'])} | "
            f"{_fmt(entry['tool_calls'])} | {quality} |"
        )
        for excluded in entry["excluded"]:
            status = excluded.get("status", f"제외: {excluded.get('stop_reason', 'unknown')}")
            lines.append(f"| {entry['scenario']} | {entry['mode']} | {status} | — | — | — | — | — | — | — | — | 미채점 |")
    lines.append("")
    lines.append("표본이 작다(n 열). 토큰 0은 호스트가 사용량을 내보내지 않았다는 뜻일 수 있다 — 원본 .events.jsonl을 확인한다.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="평가 결과를 시나리오×모드 표로 집계")
    parser.add_argument("paths", nargs="+", help="결과 폴더 또는 결과 JSON 파일")
    parser.add_argument("--out", help="마크다운 표 저장 경로(생략 시 표준 출력)")
    args = parser.parse_args(argv)
    try:
        rows = [row for row in (load_row(p) for p in collect_result_files(map(Path, args.paths))) if row]
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if not rows:
        print("결과 JSON을 찾지 못했다", file=sys.stderr)
        return 2
    text = format_table(aggregate(rows))
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
