---
type: Attested Computation
spheres: []
title: "Mean of a trailing window of the template's synthetic series (attested)"
description: "The one computation this template ships, as the shape to copy: the mean of a trailing window of a synthetic monthly series with a seeded bootstrap interval, run by the executor in the skill beside it and written as a receipt; the attester hashes the executor, regenerates the series and recomputes every number in the receipt."
tags: [example, template, attested, receipt, bootstrap, mean]
runtime: python
parameters:
  - { name: window, type: "integer: trailing months, 12 to 48", required: true }
computation: ../../skills/example-workflow/scripts/example_executor.py
executor:
  resource: ../../skills/example-workflow/scripts/example_executor.py
  receipt: [run_id, computation, code_sha256, runtime, generated_utc, data, bound_parameters, results, caveats]
attester:
  resource: ../../skills/example-workflow/scripts/example_attester.py
generated: { by: "process:template-scaffold", at: 2026-09-20T00:00:00Z }
status: draft
sources:
  - id: executor
    resource: ../../skills/example-workflow/scripts/example_executor.py
    title: "example_executor.py: the sanctioned executor, which binds the window, reads the data root and writes the receipt"
  - id: attester
    resource: ../../skills/example-workflow/scripts/example_attester.py
    title: "example_attester.py: the deterministic attester, which takes a receipt and returns a verdict with no language model in the path"
  - id: skill
    resource: ../../skills/example-workflow/SKILL.md
    title: "The run procedure an agent follows to bind a value and quote the result"
  - id: golden
    resource: ../../verification/example_workflow.py
    title: "The golden that runs the executor, the attester and the refusal on every pull request"
  - id: data-root
    resource: ../references/retrieval/example-series/SOURCES.json
    title: "Provenance of the data root the executor reads: one synthetic series, closed form and public domain"
---

# Mean of a trailing window of the template's synthetic series (attested)

A computation is a skill. The concept is here, under the capability's
own `knowledge/computations/`, because this is the package that runs
it; the code it names is in the skill beside it, the data it reads is
data under this bundle's `references/retrieval/`, and the golden that
proves the code is under `verification/`. Replace the computation, keep
the shape.

**What runs.** The executor takes the trailing `window` months of the
synthetic series, computes the mean, the sample standard deviation, the
range and a seeded bootstrap 95 percent interval on the mean, and
writes one receipt.[^executor] The seed is fixed, so two runs of the
same window agree to the last digit and the attester can recompute the
interval rather than believe it.

**What the caller may change.** Values only, for the parameters
declared above: here that is `window`, an integer from 12 to 48. The
agent does not edit the computation, does not choose the data and does
not widen the range; a window outside it is refused with the reason
code `window-out-of-range` and exit status 3, and no receipt is
written.[^skill] The runtime that ran the executor is named on the
command line and recorded in the receipt, so a result produced on one
runtime can be checked on another.

**What the receipt carries.** The fields listed in `executor.receipt`:
the run identifier, the path of the computation and the digest of the
executor file, the runtime, the time, the data root and its digest, the
bound parameters, the results and the caveats.

**What the attester checks.** Six things, deterministically and with no
language model in the path: every declared field is present; the
receipt's `code_sha256` is the executor beside it, so an edited
computation invalidates every earlier receipt by construction; the
bound window is in range and is the window the results report; the data
root regenerated from the executor's closed form hashes to the digest
the receipt and the committed file carry; every number in the results
recomputes from the regenerated series; and the mean lies inside its
own interval.[^attester] A failed check is a FAIL verdict and exit
status 1.

**What proves the code.** The golden runs the executor on the data
root, the attester on the receipt it wrote, the refusal on a window out
of range, and the attester once more on a receipt with one number
changed, which must fail.[^golden] It runs headless on every pull
request.

**The data.** One synthetic series, 48 monthly values near 1.0, written
by the executor's own generator and committed under this bundle's
`references/retrieval/` as data.[^data-root] It proves the chain and
says nothing about the world, which is what the receipt's caveat
records. A capability that reads retrieved granules keeps them in the
same place, stamped, and cites the provider bundle's concepts for what
they mean.

**Status.** Draft: the template ships no signature, and a copy signs
its own computation once a steward has reviewed it.

[^executor]: The sanctioned executor, in the skill that runs it.
[^attester]: The deterministic attester, beside the executor.
[^skill]: The run procedure the agent follows.
[^golden]: The golden that proves both scripts.
[^data-root]: The provenance of the data root the executor reads.
