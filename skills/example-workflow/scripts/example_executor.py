#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""The executor of the attested computation this template ships: the
mean of a trailing window of the synthetic monthly series, with a
seeded bootstrap interval, written as a receipt.

A computation is a skill. The concept that declares this contract is
knowledge/computations/example-workflow.md, beside the data root this
script reads; the run procedure is the SKILL.md above this directory;
the attester beside this file rechecks a receipt with no language model
in the path; verification/example_workflow.py proves both scripts.
Replace the computation, keep the shape.

The caller binds values only. `window` is the one declared parameter,
and a value outside the range the concept declares is refused (exit 3
with a reason code) rather than computed.

  example_executor.py --window 48 --runtime claude-code [--out receipt.json]
  example_executor.py --write-series      # rewrite the data root from the closed form below

Standard library only, so the header's dependency list is empty and
`uv run` resolves it anywhere.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE_ROOT = HERE.parents[2]
COMPUTATION = "skills/example-workflow/scripts/example_executor.py"
SERIES = PACKAGE_ROOT / "knowledge" / "references" / "retrieval" / "example-series" / "example_series.csv"
MONTHS = 48
WINDOW_MIN, WINDOW_MAX = 12, 48
RESAMPLES = 500
SEED = 7
REFUSED = 3


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def value_digest(value) -> str:
    blob = json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(blob).hexdigest()


def refuse(code: str, detail: str) -> None:
    """The refusal path: a bound value the contract does not allow buys a
    reason code and no receipt, never a number."""
    print(f"refused: {code}: {detail}", file=sys.stderr)
    raise SystemExit(REFUSED)


def series(months: int = MONTHS) -> list[tuple[str, float]]:
    """The synthetic series, closed form so the same bytes come out on
    every machine: monthly values from 2020-01 near 1.0 with a small
    annual cycle and a slower modulation, rounded to four decimals.
    The attester regenerates the data root from this function rather
    than trusting the file."""
    rows = []
    for i in range(months):
        value = 1.0 + 0.08 * math.sin(2 * math.pi * i / 12) + 0.02 * math.cos(2 * math.pi * i / 5)
        rows.append((f"{2020 + i // 12:04d}-{1 + i % 12:02d}", round(value, 4)))
    return rows


def write_series(path: Path, rows: list[tuple[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["month", "value"])
        writer.writerows(rows)


def read_series(path: Path) -> list[tuple[str, float]]:
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != ["month", "value"]:
            refuse("data-root-malformed", f"{path} has columns {reader.fieldnames}, expected month and value")
        return [(row["month"], float(row["value"])) for row in reader]


def summarize(rows: list[tuple[str, float]], window: int) -> dict:
    """The computation: the mean of the trailing `window` months with a
    seeded bootstrap 95 percent interval, plus the descriptive numbers.
    The seed is fixed, so the interval is the same on every run and the
    attester can recompute it exactly."""
    values = [value for _, value in rows[-window:]]
    rng = random.Random(SEED)
    means = sorted(statistics.fmean(rng.choices(values, k=window)) for _ in range(RESAMPLES))
    lo, hi = means[int(0.025 * (RESAMPLES - 1))], means[int(0.975 * (RESAMPLES - 1))]
    return {
        "n": window,
        "first_month": rows[-window][0],
        "last_month": rows[-1][0],
        "mean": statistics.fmean(values),
        "stdev": statistics.stdev(values),
        "min": min(values),
        "max": max(values),
        "ci95": [lo, hi],
        "resamples": RESAMPLES,
        "seed": SEED,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--window", type=int, help=f"the declared parameter: trailing months, {WINDOW_MIN} to {WINDOW_MAX}")
    ap.add_argument("--runtime", help="the runtime that ran this (claude-code, claude-cowork, openai-codex, ...)")
    ap.add_argument("--runtime-version", default=None)
    ap.add_argument("--out", type=Path, default=Path("receipt.json"))
    ap.add_argument("--write-series", action="store_true", help="rewrite the data root from the closed form and stop")
    args = ap.parse_args(argv)

    if args.write_series:
        write_series(SERIES, series())
        print(f"wrote {SERIES} ({MONTHS} rows)")
        return 0
    if args.window is None or not args.runtime:
        ap.error("--window and --runtime are required unless --write-series is given")
    if not WINDOW_MIN <= args.window <= WINDOW_MAX:
        refuse("window-out-of-range", f"window {args.window} is outside {WINDOW_MIN} to {WINDOW_MAX}")

    rows = read_series(SERIES)
    if len(rows) < args.window:
        refuse("data-root-too-short", f"the data root holds {len(rows)} months, window {args.window}")

    receipt = {
        "computation": COMPUTATION,
        "code_sha256": sha256_file(Path(__file__).resolve()),
        "runtime": {"name": args.runtime, "version": args.runtime_version},
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "data": {"root": "knowledge/references/retrieval/example-series", "series": SERIES.name,
                 "sha256": sha256_file(SERIES), "n_rows": len(rows)},
        "bound_parameters": {"window": args.window},
        "results": summarize(rows, args.window),
        "caveats": ["a synthetic series (public domain), not observations: the numbers prove the chain, not a claim about the world"],
    }
    receipt["run_id"] = value_digest({k: v for k, v in receipt.items() if k != "generated_utc"})[:23]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    r = receipt["results"]
    print(f"window {r['n']} months ({r['first_month']} to {r['last_month']}) on {args.runtime}: "
          f"mean {r['mean']:.4f} (95% bootstrap CI {r['ci95'][0]:.4f} to {r['ci95'][1]:.4f}); "
          f"receipt {args.out} run {receipt['run_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
