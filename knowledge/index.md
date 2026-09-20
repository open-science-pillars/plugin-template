---
okf_version: "0.2"
sphere_scope: cross-cutting
---

# Bundle index

The capability's own bundle: what a steward signs. It holds knowledge
and evidence and no runnable code. OKF v0.2 conformant (okf_version
"0.2" above). List every concept here as it lands; the
knowledge-linter flags concepts unreachable from index.md. The
scaffold declares `sphere_scope: cross-cutting`, which is what lets a
concept carry an empty `spheres` list; a domain capability names its
spheres on every concept and drops that line. Concepts of every other
type (datasets, gotchas, recipes, conventions) start from
[knowledge-template](https://github.com/open-science-pillars/knowledge-template),
which carries an annotated example of each.

## computations

The computations this capability runs. A computation is a skill: the
concept is here, the executor and the attester it names are in the
skill that runs them, under `skills/<name>/scripts/`, and the golden
that proves them is under `verification/`.

- [Mean of a trailing window of the template's synthetic series (attested)](computations/example-workflow.md), type: Attested Computation, status: draft, run by the skill example-workflow

## references

Mirrored external material and the evidence a concept cites, as data.
`references/retrieval/example-series/` is the data root the example
computation reads: one synthetic series with its provenance stamp in
`SOURCES.json`. A capability that reads retrieved granules keeps them,
their stamps and their record files here in the same way.

## Provider bundles (declared dependencies)

None yet. A plugin that consults a provider bundle declares it under
`dependencies.knowledge` in `.osp/package.yaml` with a version floor
(the plugin manifest is rendered from that file, never edited) and
describes it here under its own heading: the canonical home, how it is consulted
(the core skill consult-knowledge finds every installed bundle through
the installer's record; skills and agents cite provider concepts by
bundle path, `knowledge/<bundle>/<type>/<concept>.md`), and the
precedence rule (the provider concept wins on conflict; `stable`
outranks `draft`; a draft is voiced as a draft). Nothing from a
provider bundle is copied into this one. The provider bundle is the
authority on products; this capability is the authority on the methods
its computations define.
