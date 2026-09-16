---
name: example-workflow
description: Annotated example workflow skill for the plugin template. Summarize a small series with its helper script (mean and a bootstrap interval) behind a confirmation gate before writing output.
---

# example-workflow

An annotated example of a workflow skill. Replace everything, keep the
shape. The shape is what the org's rules check.

## Why the frontmatter looks like that

`name` plus a `description` of 200 characters or fewer, keyword-first: the
description is what surfaces match a user's request against, and skill
descriptions share a context budget, so front-load the words a
scientist would actually use. Workflow skills leave both invocation paths
open: a user can invoke `/your-plugin:example-workflow` on Claude Code or
just describe the task conversationally on any surface. Never set
`disable-model-invocation: true` on a workflow skill.

## Why there is a scripts/ directory

A script a skill runs at runtime lives in that skill's `scripts/`
directory, beside this file, and the skill invokes it through the
plugin root, never by a path relative to the working directory (the
placement rule, ADR C in the marketplace repository's docs/decisions).
Every file of code has one home by plane: sanctioned code a concept
names stays in the knowledge bundle, a procedure is a skill, a runtime
helper is in that skill's `scripts/`, and the goldens and their frozen
fixtures are in the goldens' own tree, which no skill names. This
skill's helper is `scripts/example_helper.py`: it summarizes one column
of a small CSV series (count, mean, sample standard deviation, range and
a seeded bootstrap 95 percent interval on the mean), carries a PEP 723
header so `uv run` resolves it on any machine, and has a `--selftest`.

## Behavior

1. Restate the request as parameters (input file, column, period) and
   consult the plugin's knowledge bundle for concepts about the target
   dataset; surface applicable gotchas before computing.
2. Compute with the helper, passing the input the user named:

   ```bash
   uv run ${CLAUDE_PLUGIN_ROOT}/skills/example-workflow/scripts/example_helper.py <series.csv> --column value
   ```

   Add `--json` when the numbers feed a later step. Declare compute
   needs rather than assuming a terminal: small (laptop), medium (Dask),
   large (HPC); this example is small.
3. **Confirmation gate (the pattern that matters):** before any side effect
   (writing a file, downloading data above the volume threshold), show what
   will happen (filename, size, destination) and wait for an explicit yes.
   The gate lives here in the skill body so it fires on every surface.
4. Report the result with an uncertainty statement (the helper's
   bootstrap interval, or the uncertainty the recipe concept prescribes),
   or a one-line reason why none is available (the house reporting rule).

## Must NOT

- Write or download anything before the gate.
- Present a headline number without uncertainty framing.
- Reference files outside this plugin's directory (self-containment).
- Name or run anything in the goldens' tree: a helper the skill needs is
  in `scripts/`, and the placement gate fails a skill that points at a
  golden or a fixture.

## Verification

This skill's computational recipe is regression-tested by the golden
notebook for this workflow, a marimo notebook that runs headless in the
goldens workflow and exits nonzero on assertion failure. It runs the same
computation on the frozen fixtures, imports this skill's helper by path
and asserts that the two agree on the expected value and its uncertainty
range. A workflow skill without a green golden notebook is not done.
