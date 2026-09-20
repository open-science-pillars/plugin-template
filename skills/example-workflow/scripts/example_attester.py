#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""The attester of the attested computation this template ships: it
takes a receipt written by example_executor.py and returns a verdict,
deterministically and with no language model in the path.

A receipt attests PASS (exit 0) only when all of these hold, else FAIL
(exit 1) naming the check that broke:

  fields     every field the concept declares is in the receipt;
  code       the receipt's code_sha256 is the executor beside this
             file, so an edited computation invalidates every earlier
             receipt by construction;
  parameter  the bound window is the one value the receipt reports and
             lies in the range the concept declares;
  data       the data root regenerated here from the executor's closed
             form hashes to the receipt's digest, and so does the
             committed file the executor read;
  recompute  every number in the receipt's results, recomputed from
             the regenerated series, equals what the receipt says;
  plausible  the mean lies inside its own interval and the interval
             has a width a bootstrap on this series can produce.

  example_attester.py RECEIPT.json [--out attestation.json]
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import math
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTESTER = "skills/example-workflow/scripts/example_attester.py"
SPEC = importlib.util.spec_from_file_location("example_executor", HERE / "example_executor.py")
ex = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ex)

FIELDS = ["run_id", "computation", "code_sha256", "runtime", "generated_utc", "data",
          "bound_parameters", "results", "caveats"]
TOL = 1e-12


def close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=TOL, abs_tol=TOL)


def same(recomputed, reported) -> bool:
    """A recomputed value against the one the receipt reports: floats to
    a tolerance, lists element by element, anything else exactly."""
    if isinstance(recomputed, float) and isinstance(reported, (int, float)):
        return close(recomputed, float(reported))
    if isinstance(recomputed, list) and isinstance(reported, list) and len(recomputed) == len(reported):
        return all(same(x, y) for x, y in zip(recomputed, reported))
    return recomputed == reported


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("receipt", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    checks: list[dict] = []

    def check(name: str, ok: bool, detail: str) -> None:
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    missing = [f for f in FIELDS if f not in receipt]
    check("fields", not missing, "all present" if not missing else f"missing {missing}")

    sanctioned = ex.sha256_file(HERE / "example_executor.py")
    check("code", receipt.get("code_sha256") == sanctioned,
          f"receipt {receipt.get('code_sha256')} against sanctioned {sanctioned}")

    results = receipt.get("results") or {}
    window = (receipt.get("bound_parameters") or {}).get("window")
    check("parameter", isinstance(window, int) and ex.WINDOW_MIN <= window <= ex.WINDOW_MAX
          and window == results.get("n"),
          f"window {window} in {ex.WINDOW_MIN} to {ex.WINDOW_MAX}, results report n {results.get('n')}")

    rows = ex.series()
    with tempfile.TemporaryDirectory() as tmp:
        regenerated = Path(tmp) / ex.SERIES.name
        ex.write_series(regenerated, rows)
        digest = ex.sha256_file(regenerated)
    committed = ex.sha256_file(ex.SERIES) if ex.SERIES.is_file() else None
    check("data", digest == (receipt.get("data") or {}).get("sha256") == committed,
          f"regenerated {digest}, receipt {(receipt.get('data') or {}).get('sha256')}, committed {committed}")

    if isinstance(window, int) and ex.WINDOW_MIN <= window <= min(ex.WINDOW_MAX, len(rows)):
        fresh = ex.summarize(rows, window)
        drift = [key for key, value in fresh.items() if not same(value, results.get(key))]
        check("recompute", not drift, f"{len(fresh)} values recompute" if not drift else f"drift in {drift}")
    else:
        check("recompute", False, "no usable window to recompute from")

    mean, ci = results.get("mean"), results.get("ci95") or [None, None]
    check("plausible", None not in (mean, ci[0], ci[1]) and ci[0] < mean < ci[1] and 0 < ci[1] - ci[0] < 0.1,
          f"mean {mean} inside [{ci[0]}, {ci[1]}]" if None not in (mean, ci[0], ci[1]) else "mean or interval missing")

    verdict = "PASS" if all(c["ok"] for c in checks) else "FAIL"
    attestation = {
        "verdict": verdict,
        "attester": ATTESTER,
        "attester_sha256": ex.sha256_file(Path(__file__).resolve()),
        "computation_sha256": sanctioned,
        "receipt": args.receipt.name,
        "receipt_sha256": ex.sha256_file(args.receipt),
        "run_id": receipt.get("run_id"),
        "runtime": receipt.get("runtime"),
        "attested_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "checks": checks,
    }
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(attestation, indent=2) + "\n", encoding="utf-8")
    for c in checks:
        print(f"  {'ok  ' if c['ok'] else 'FAIL'} {c['name']}: {c['detail']}")
    print(f"{verdict}: run {receipt.get('run_id')} on {(receipt.get('runtime') or {}).get('name')}"
          + (f", attestation {args.out}" if args.out else ""))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
