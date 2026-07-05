---
name: example-workflow
description: Annotated example workflow skill for the plugin template. Compute a small demonstration statistic from a fixture with a confirmation gate before writing output.
---

# example-workflow

An annotated example of a workflow skill. Replace everything, keep the
shape. The shape is what the org's rules check.

## Why the frontmatter looks like that

`name` plus a `description` of 200 characters or fewer, keyword-first: the
description is what surfaces match a user's request against, and skill
descriptions share a context budget (SPEC §0.3), so front-load the words a
scientist would actually use. Workflow skills leave both invocation paths
open: a user can invoke `/your-plugin:example-workflow` on Claude Code or
just describe the task conversationally on any surface. Never set
`disable-model-invocation: true` on a workflow skill.

## Behavior

1. Restate the request as parameters (input, region, period) and consult
   the plugin's knowledge bundle for concepts about the target dataset;
   surface applicable gotchas before computing.
2. Compute. Declare compute needs rather than assuming a terminal: small
   (laptop), medium (Dask), large (HPC) per SPEC §0.4.
3. **Confirmation gate (the pattern that matters):** before any side effect
   (writing a file, downloading data above the volume threshold), show what
   will happen (filename, size, destination) and wait for an explicit yes.
   The gate lives here in the skill body so it fires on every surface.
4. Report the result with an uncertainty statement, or a one-line reason
   why none is available (the house reporting rule).

## Must NOT

- Write or download anything before the gate.
- Present a headline number without uncertainty framing.
- Reference files outside this plugin's directory (self-containment, §0.5).

## Verification

This skill's computational recipe is regression-tested by
`verification/example_workflow.py`, a marimo golden notebook that runs
headless and exits nonzero on assertion failure. A workflow skill without
a green golden notebook is not done.
