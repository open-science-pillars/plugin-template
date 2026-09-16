# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Summarize one column of a small CSV series: count, mean, sample
standard deviation, minimum, maximum, and a bootstrap 95 percent
confidence interval on the mean. This is the one honest thing the
example workflow computes, so the skill has a script to run and the
golden notebook has the same computation to check.

A script a skill runs at runtime lives in that skill's scripts/
directory, beside its SKILL.md, and the skill invokes it through the
plugin root (the placement rule, ADR C). It is not sanctioned code (no
concept names it, no receipt hashes it), so it does not live in the
knowledge bundle; and it is not a golden, so it does not live with
the goldens.

  uv run ${CLAUDE_PLUGIN_ROOT}/skills/example-workflow/scripts/example_helper.py PATH [--column value] [--json]
  uv run ${CLAUDE_PLUGIN_ROOT}/skills/example-workflow/scripts/example_helper.py --selftest

Standard library only, so the header's dependency list is empty and
`uv run` resolves it anywhere.
"""

import argparse
import csv
import json
import random
import statistics
import sys
import tempfile
from pathlib import Path

RESAMPLES = 500
SEED = 7


def read_column(path: Path, column: str = "value") -> list[float]:
    """The numeric values of one named column of a CSV file with a header row."""
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or column not in reader.fieldnames:
            raise SystemExit(f"{path}: no column named {column!r} (columns: {reader.fieldnames})")
        try:
            return [float(row[column]) for row in reader]
        except ValueError as exc:
            raise SystemExit(f"{path}: a value in column {column!r} is not a number: {exc}") from exc


def summarize(values: list[float], resamples: int = RESAMPLES, seed: int = SEED) -> dict:
    """Mean with a seeded bootstrap 95 percent interval, plus the plain
    descriptive numbers. The seed is fixed so the interval is the same
    on every run; it is a demonstration of result-plus-uncertainty,
    not a substitute for the uncertainty a real recipe prescribes."""
    if len(values) < 2:
        raise SystemExit("a summary needs at least two values")
    rng = random.Random(seed)
    means = sorted(statistics.fmean(rng.choices(values, k=len(values))) for _ in range(resamples))
    lo = means[int(0.025 * (resamples - 1))]
    hi = means[int(0.975 * (resamples - 1))]
    return {
        "n": len(values),
        "mean": statistics.fmean(values),
        "stdev": statistics.stdev(values),
        "min": min(values),
        "max": max(values),
        "ci95": [lo, hi],
        "resamples": resamples,
        "seed": seed,
    }


def render(summary: dict, path: Path, column: str) -> str:
    lo, hi = summary["ci95"]
    return (
        f"{path} column {column!r}: n={summary['n']}, mean={summary['mean']:.4f} "
        f"(95% bootstrap CI {lo:.4f} to {hi:.4f}, {summary['resamples']} resamples), "
        f"stdev={summary['stdev']:.4f}, min={summary['min']:.4f}, max={summary['max']:.4f}"
    )


def selftest() -> int:
    ok = True

    def check(cond: bool, what: str) -> None:
        nonlocal ok
        print(f"  {'ok ' if cond else 'FAIL'} {what}")
        ok = ok and cond

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "series.csv"
        path.write_text("month,value\n2020-01,1\n2020-02,2\n2020-03,3\n2020-04,4\n")
        values = read_column(path)
        check(values == [1.0, 2.0, 3.0, 4.0], "read_column returns the column as floats")
        summary = summarize(values)
        check(summary["n"] == 4 and summary["mean"] == 2.5, "mean of 1..4 is 2.5")
        check(abs(summary["stdev"] - statistics.stdev(values)) < 1e-12, "sample standard deviation")
        check(summary["min"] == 1.0 and summary["max"] == 4.0, "min and max")
        lo, hi = summary["ci95"]
        check(lo <= summary["mean"] <= hi, "the mean lies inside its own bootstrap interval")
        check(summarize(values)["ci95"] == summary["ci95"], "the seeded interval is reproducible")
        check(lo >= 1.0 and hi <= 4.0, "the interval stays within the range of the data")
    print("selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", type=Path, help="a CSV file with a header row")
    ap.add_argument("--column", default="value", help="the column to summarize (default: value)")
    ap.add_argument("--json", action="store_true", help="print the summary as JSON")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.path is None:
        ap.error("a CSV path is required unless --selftest is given")
    summary = summarize(read_column(args.path, args.column))
    if args.json:
        print(json.dumps({"path": str(args.path), "column": args.column, **summary}, indent=2))
    else:
        print(render(summary, args.path, args.column))
    return 0


if __name__ == "__main__":
    sys.exit(main())
