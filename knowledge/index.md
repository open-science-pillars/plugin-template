---
okf_version: "0.2"
---

# Bundle index

Empty conformant bundle: start from the knowledge-template repo, which
carries four annotated example concepts under knowledge/ and points at
the marketplace repository's docs/contributing-knowledge.md and
docs/okf-conformance.md. OKF v0.2 conformant (okf_version "0.2"
above). List every concept here as it lands; the
knowledge-linter flags concepts unreachable from index.md.

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
provider bundle is copied into this one.
