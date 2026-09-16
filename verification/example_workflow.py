# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "numpy",
# ]
# ///
# The golden notebook of the example workflow: the pattern every workflow
# skill copies. It runs headless (`uv run verification/example_workflow.py`)
# and exits nonzero on assertion failure; .github/workflows/goldens.yml
# runs every notebook at the top of verification/ on every pull request.
#
# It reads the frozen fixture under verification/fixtures/ (provenance in
# the README there), runs the same computation the skill's helper script
# runs (skills/example-workflow/scripts/example_helper.py, imported by
# path), and asserts the expected value and its expected-uncertainty
# range. A real notebook does the same with the skill's canonical
# computation and the ranges its recipe concept records. The direction
# matters (the placement rule, ADR C): a golden may import a skill's
# script, and no skill ever names anything under verification/.

import marimo

__generated_with = "0.23.13"
app = marimo.App()


@app.cell
def _():
    import csv
    import importlib.util
    from pathlib import Path

    import numpy as np

    return Path, csv, importlib, np


@app.cell
def _(Path):
    # Paths are resolved from this file, so the notebook runs from any
    # working directory: the fixture beside it, the helper in its skill.
    root = Path(__file__).resolve().parents[1]
    fixture = root / "verification" / "fixtures" / "example_series.csv"
    helper_path = root / "skills" / "example-workflow" / "scripts" / "example_helper.py"
    assert fixture.is_file(), f"missing fixture {fixture}"
    assert helper_path.is_file(), f"missing helper {helper_path}"
    return fixture, helper_path


@app.cell
def _(csv, fixture, np):
    # Load the fixture. 48 monthly values near 1.0 (fixtures/README.md).
    with fixture.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    series = np.array([float(r["value"]) for r in rows])
    assert series.size == 48, f"expected 48 rows, read {series.size}"
    assert rows[0]["month"] == "2020-01" and rows[-1]["month"] == "2023-12"
    return (series,)


@app.cell
def _(np, series):
    # The computation this example skill encodes: a mean with a bootstrap
    # confidence interval, the minimal shape of result-plus-uncertainty.
    rng = np.random.default_rng(seed=7)
    boot = np.array([
        rng.choice(series, size=series.size, replace=True).mean()
        for _ in range(500)
    ])
    lo, hi = np.percentile(boot, [2.5, 97.5])
    mean = series.mean()

    # Assertions are the gate: expected value AND its uncertainty range.
    assert abs(mean - 1.0002) < 5e-4, f"mean {mean:.4f} is not the fixture's 1.0002"
    assert lo < mean < hi, "mean must lie inside its own bootstrap CI"
    assert 0.02 < (hi - lo) < 0.05, f"CI width {hi - lo:.4f} outside the expected 0.02 to 0.05"
    return hi, lo, mean


@app.cell
def _(fixture, helper_path, hi, importlib, lo, mean, series):
    # The skill's helper runs the same workflow on the same fixture and
    # must agree with the notebook: same count, same mean, and an
    # interval of the same width to the tolerance a bootstrap allows.
    spec = importlib.util.spec_from_file_location("example_helper", helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    summary = helper.summarize(helper.read_column(fixture))
    assert summary["n"] == series.size
    assert abs(summary["mean"] - mean) < 1e-9, f"helper mean {summary['mean']} differs from {mean}"
    h_lo, h_hi = summary["ci95"]
    assert abs((h_hi - h_lo) - (hi - lo)) < 0.01, "helper and notebook intervals disagree in width"
    print(f"example workflow: n={summary['n']} mean={mean:.4f} CI {lo:.4f} to {hi:.4f}; helper agrees")
    return


if __name__ == "__main__":
    app.run()
