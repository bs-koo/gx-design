#!/usr/bin/env python3
"""Report reviewed first-useful/rework turns without guessing from model prose.

python evals/benchmark.py results/T17-core.json [more-result.json ...] [--json]
Each result needs a sibling .review.json with reviewer, evidence,
first_useful_turn (1-based or null) and rework_turns (unique turn numbers).
No model calls or result mutations. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys


def _seconds(value, label: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{label}: expected finite nonnegative seconds or null")
    return float(value)


def _turn(value, count: int) -> int:
    if type(value) is not int or not 1 <= value <= count:
        raise ValueError(f"turn must be a recorded 1-based integer (1..{count})")
    return value


def _sum_known(values: list[float | None]) -> float | None:
    return sum(values) if all(value is not None for value in values) else None


def summarize(result: dict, review: dict) -> dict:
    """Time is CLI active time through a reviewed turn, not human waiting time.

    The first useful output could occur earlier within the selected turn, hence
    the upper-bound label. Usefulness and rework require independent judgment.
    Missing timing stays unknown; completed state never implies usefulness.
    """
    if not isinstance(result, dict) or not isinstance(review, dict):
        raise ValueError("result and review must be objects")
    for key in ("scenario", "mode"):
        if not isinstance(result.get(key), str) or not result[key].strip():
            raise ValueError(f"result requires {key}")
    for key in ("reviewer", "evidence"):
        if not isinstance(review.get(key), str) or not review[key].strip():
            raise ValueError(f"review requires nonempty {key}")
    if "first_useful_turn" not in review or "rework_turns" not in review:
        raise ValueError("review requires first_useful_turn (or null) and rework_turns")
    turns = result.get("turns")
    if not isinstance(turns, list) or any(not isinstance(turn, dict) for turn in turns):
        raise ValueError("result requires a list of recorded turns")
    elapsed = []
    for index, turn in enumerate(turns, 1):
        if "turn" in turn and (type(turn["turn"]) is not int or turn["turn"] != index):
            raise ValueError("recorded turns must be consecutive and 1-based")
        elapsed.append(_seconds(turn.get("elapsed_seconds"), f"turn {index}"))
    first = review["first_useful_turn"]
    if first is not None:
        first = _turn(first, len(turns))
    rework = review["rework_turns"]
    if not isinstance(rework, list):
        raise ValueError("rework_turns must be a list")
    for turn in rework:
        _turn(turn, len(turns))
    if len(rework) != len(set(rework)):
        raise ValueError("rework_turns must not contain duplicates")
    return {
        "scenario": result["scenario"], "mode": result["mode"],
        "stop_reason": result.get("stop_reason", "unknown"),
        "first_useful_turn": first,
        "first_useful_cli_seconds_upper_bound": _sum_known(elapsed[:first]) if first is not None else None,
        "rework_turns": sorted(rework), "rework_turn_count": len(rework),
        "rework_cli_seconds": _sum_known([elapsed[turn - 1] for turn in rework]),
        "total_cli_seconds": _sum_known(elapsed) if elapsed else None,
        "total_elapsed_seconds": _seconds(result.get("elapsed_seconds"), "elapsed_seconds"),
        "timing_complete": bool(elapsed) and all(value is not None for value in elapsed),
        "timing_basis": "reviewed_turn_boundaries",
        "reviewer": review["reviewer"], "evidence": review["evidence"],
    }


def _cell(value) -> str:
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def format_report(rows: list[dict]) -> str:
    def seconds(value):
        return "미측정" if value is None else f"{value:.2f}"

    lines = ["| 시나리오 | 모드 | 종료 상태 | 전체 경과(초) | CLI 합계(초) | 첫 유용결과 CLI 상한(초) | 재작업 턴 | 재작업 CLI(초) | 검토자 |",
             "|---|---|---|---|---|---|---|---|---|"]
    for row in rows:
        cells = [row["scenario"], row["mode"], row["stop_reason"], seconds(row["total_elapsed_seconds"]),
                 seconds(row["total_cli_seconds"]), seconds(row["first_useful_cli_seconds_upper_bound"]),
                 row["rework_turn_count"], seconds(row["rework_cli_seconds"]), row["reviewer"]]
        lines.append("| " + " | ".join(map(_cell, cells)) + " |")
    lines.extend(["", "첫 유용결과는 검토자가 지정한 턴 종료까지의 CLI 실행시간 상한이다. 실제 사람의 응답 대기시간은 포함하지 않는다.",
                  "재작업 횟수는 검토자가 지정한 턴 수이며 턴 내부 수정 횟수가 아니다. 비교하려면 같은 과업·모델·호스트·데이터·환경에서 반복 표본을 확보한다."])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="첫 유용결과와 재작업의 검토 기반 시간 보고서")
    parser.add_argument("results", nargs="+", type=Path, help="결과 JSON 파일; 옆의 .review.json 필요")
    parser.add_argument("--json", action="store_true", help="근거를 포함한 JSON 출력")
    parser.add_argument("--out", type=Path, help="선택 저장 경로")
    args = parser.parse_args(argv)
    try:
        rows = []
        for path in args.results:
            data = json.loads(path.read_text(encoding="utf-8"))
            review_path = path.with_suffix(".review.json")
            review = json.loads(review_path.read_text(encoding="utf-8"))
            rows.append(dict(summarize(data, review), source=str(path)))
        output = json.dumps(rows, ensure_ascii=False, indent=2) if args.json else format_report(rows)
        if args.out:
            protected = {path.resolve() for path in args.results}
            protected.update(path.with_suffix(".review.json").resolve() for path in args.results)
            if args.out.resolve() in protected:
                raise ValueError("output must not overwrite a result or review file")
            args.out.write_text(output + "\n", encoding="utf-8")
        else:
            print(output)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
