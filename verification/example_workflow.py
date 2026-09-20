# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
# ]
# ///
# The golden of the example computation: the pattern every skill with a
# script copies. It runs headless (`uv run verification/example_workflow.py`)
# and exits nonzero on assertion failure; .github/workflows/goldens.yml
# runs every notebook at the top of verification/ on every pull request.
#
# What proves a script is under verification/. This golden names both
# scripts of the attested computation declared by
# knowledge/computations/example-workflow.md and exercises the whole
# contract: the executor on the committed data root, the attester on the
# receipt it wrote, the refusal on a bound value outside its range, and
# the attester once more on a receipt with one number changed, which must
# fail. The direction is one way: a golden names a skill's scripts, and
# no skill names anything under verification/.

import marimo

__generated_with = "0.23.13"
app = marimo.App()


@app.cell
def _():
    import json
    import subprocess
    import sys
    import tempfile
    from pathlib import Path

    return Path, json, subprocess, sys, tempfile


@app.cell
def _(Path):
    # Paths are resolved from this file, so the golden runs from any
    # working directory.
    root = Path(__file__).resolve().parents[1]
    scripts = root / "skills" / "example-workflow" / "scripts"
    executor = scripts / "example_executor.py"
    attester = scripts / "example_attester.py"
    concept = root / "knowledge" / "computations" / "example-workflow.md"
    data_root = root / "knowledge" / "references" / "retrieval" / "example-series"
    for required in (executor, attester, concept, data_root / "example_series.csv"):
        assert required.exists(), f"missing {required}"
    return attester, executor


@app.cell
def _(Path, subprocess, sys, tempfile):
    def run(script: Path, *args: str):
        """Run one of the computation's scripts the way a runtime would."""
        return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)

    work = Path(tempfile.mkdtemp())
    return run, work


@app.cell
def _(executor, json, run, work):
    # The executor on the committed data root: one receipt, exit 0.
    receipt_path = work / "receipt.json"
    done = run(executor, "--window", "48", "--runtime", "golden", "--out", str(receipt_path))
    assert done.returncode == 0, f"executor failed: {done.stderr}"
    receipt = json.loads(receipt_path.read_text())
    for field in ("run_id", "code_sha256", "bound_parameters", "results"):
        assert field in receipt, f"receipt is missing {field}"
    assert receipt["bound_parameters"] == {"window": 48}
    results = receipt["results"]
    assert results["n"] == 48, f"expected 48 months, receipt says {results['n']}"
    assert abs(results["mean"] - 1.0002) < 5e-4, f"mean {results['mean']:.4f} is not the series' 1.0002"
    lo, hi = results["ci95"]
    assert lo < results["mean"] < hi, "the mean must lie inside its own bootstrap interval"
    assert 0.02 < hi - lo < 0.05, f"interval width {hi - lo:.4f} outside the expected 0.02 to 0.05"
    return receipt, receipt_path, results


@app.cell
def _(attester, receipt, receipt_path, run):
    # The attester on that receipt: PASS, exit 0, every check reported.
    attested = run(attester, str(receipt_path))
    assert attested.returncode == 0, f"attester did not pass a good receipt:\n{attested.stdout}{attested.stderr}"
    assert "PASS" in attested.stdout
    for check in ("fields", "code", "parameter", "data", "recompute", "plausible"):
        assert f"ok   {check}" in attested.stdout, f"the attester did not report {check}:\n{attested.stdout}"
    print(f"attested run {receipt['run_id']}")
    return


@app.cell
def _(executor, run, work):
    # The refusal: a bound value outside the range the concept declares
    # buys a reason code and exit 3, and writes no receipt.
    refused_path = work / "refused.json"
    refused = run(executor, "--window", "4", "--runtime", "golden", "--out", str(refused_path))
    assert refused.returncode == 3, f"expected exit 3, got {refused.returncode}"
    assert "window-out-of-range" in refused.stderr, refused.stderr
    assert not refused_path.exists(), "a refusal must not write a receipt"
    return


@app.cell
def _(attester, json, receipt, run, work):
    # A receipt with one number changed must not attest: this is what
    # makes the PASS above worth quoting.
    tampered_path = work / "tampered.json"
    tampered = json.loads(json.dumps(receipt))
    tampered["results"]["mean"] += 0.01
    tampered_path.write_text(json.dumps(tampered, indent=2))
    verdict = run(attester, str(tampered_path))
    assert verdict.returncode == 1, "the attester passed a tampered receipt"
    assert "FAIL recompute" in verdict.stdout, verdict.stdout
    print("example computation: executor, attester, refusal and tamper all behave")
    return


if __name__ == "__main__":
    app.run()
