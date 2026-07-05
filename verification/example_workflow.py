# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "numpy",
# ]
# ///
# Trivial green golden notebook: the pattern every workflow skill copies.
# Runs headless via `python verification/example_workflow.py` or
# `uv run verification/example_workflow.py`; exits nonzero on assertion
# failure (verified in Session 0b). Real notebooks load a fixture from
# verification/fixtures/, run the skill's canonical computation, and assert
# expected values and expected-uncertainty ranges from the recipe concept.

import marimo

__generated_with = "0.23.13"
app = marimo.App()


@app.cell
def _():
    import numpy as np

    return (np,)


@app.cell
def _(np):
    # Synthesize a tiny deterministic fixture in-notebook (SPEC §6 allows
    # in-notebook synthesis for small inputs; larger fixtures live in
    # verification/fixtures/ with a provenance README).
    rng = np.random.default_rng(seed=42)
    series = rng.normal(loc=1.0, scale=0.1, size=240)
    return (series,)


@app.cell
def _(np, series):
    # The "computation" this example skill encodes: a mean with a bootstrap
    # confidence interval, the minimal shape of result-plus-uncertainty.
    rng2 = np.random.default_rng(seed=7)
    boot = np.array([
        rng2.choice(series, size=series.size, replace=True).mean()
        for _ in range(500)
    ])
    lo, hi = np.percentile(boot, [2.5, 97.5])
    mean = series.mean()

    # Assertions are the gate: expected value AND its uncertainty range.
    assert 0.95 < mean < 1.05, f"mean {mean:.3f} outside expected range"
    assert lo < mean < hi, "mean must lie inside its own bootstrap CI"
    assert (hi - lo) < 0.05, f"CI width {hi - lo:.4f} implausibly wide"
    return (mean, lo, hi)


if __name__ == "__main__":
    app.run()
