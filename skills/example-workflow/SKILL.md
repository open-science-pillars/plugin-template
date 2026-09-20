---
name: example-workflow
description: Annotated example of a computation that is a skill. Run the attested mean of a trailing window of the template's synthetic series, attest the receipt, and quote the number with its interval.
---

# example-workflow

An annotated example of a skill that runs an attested computation.
Replace everything, keep the shape. The shape is what the
organization's rules check.

## Why the frontmatter looks like that

`name` plus a `description` of 200 characters or fewer, keyword-first:
the description is what surfaces match a user's request against, and
skill descriptions share a context budget, so front-load the words a
scientist would actually use. Workflow skills leave both invocation
paths open: a user can invoke `/your-plugin:example-workflow` on Claude
Code or just describe the task conversationally on any surface. Never
set `disable-model-invocation: true` on a workflow skill.

## What this skill is

A computation is a skill. The concept that declares the contract is
`knowledge/computations/example-workflow.md` in this package: it names
the runtime, the one parameter you may bind, the executor, the fields
the receipt carries and the attester. The code it names is in
`scripts/` beside this file, the data the executor reads is under
`knowledge/references/retrieval/example-series/`, and the golden that
proves the scripts is `verification/example_workflow.py`. Cite the
concept by that path whenever you report a number from it.

## Behavior

1. Restate the request as the parameter the concept declares. Here that
   is `window`, the trailing months to summarize, an integer from 12 to
   48. Bind a value; never edit the computation, choose other data or
   widen the range. A window outside the range is refused by the
   executor with the reason code `window-out-of-range` and exit status
   3: report the refusal and the range, and do not work around it.
2. Run the executor, passing the name of the runtime you are running on
   (`claude-code`, `claude-cowork`, `openai-codex`) so the receipt
   records where the number came from:

   ```bash
   uv run ${CLAUDE_PLUGIN_ROOT}/skills/example-workflow/scripts/example_executor.py \
     --window 48 --runtime claude-code --out receipt.json
   ```

3. **Confirmation gate (the pattern that matters):** the executor writes
   a receipt, which is a file. Before any side effect (writing a file,
   downloading data above the volume threshold), show what will happen
   (filename, size, destination) and wait for an explicit yes. The gate
   lives here in the skill body so it fires on every surface.
4. Attest before quoting. Run the attester on the receipt and read its
   verdict:

   ```bash
   uv run ${CLAUDE_PLUGIN_ROOT}/skills/example-workflow/scripts/example_attester.py receipt.json
   ```

   PASS with exit status 0, or FAIL with exit status 1 naming the check
   that broke.
5. Report the result with its uncertainty (the receipt's `ci95`) and
   cite the concept by path, `knowledge/computations/example-workflow.md`,
   with the run identifier from the receipt. Declare compute needs
   rather than assuming a terminal: small (laptop), medium (Dask),
   large (HPC); this example is small.

## Must NOT

- Quote a number from a receipt that has not attested PASS.
- Write or download anything before the gate.
- Present a headline number without uncertainty framing.
- Edit the computation, bind an undeclared parameter, or point the
  executor at other data: the agent supplies values, nothing else.
- Reference files outside this plugin's directory (self-containment),
  or reach into `verification/`: the golden proves the scripts, and
  nothing here runs it.

## Verification

`verification/example_workflow.py` runs the executor on the data root,
the attester on the receipt it wrote, the refusal on a window out of
range, and the attester once more on a receipt with one number changed,
which must fail. It runs headless in the goldens workflow and exits
nonzero on an assertion failure. A skill that runs a computation is not
done until its golden is green.
