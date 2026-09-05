# plugin-template

The scaffold for new Open Science Pillars domain plugins. Copy it, rename,
and replace the examples. Skills-only structure: there is NO `commands/`
directory anywhere in this org (everything is a skill; skills unification
of 2026-01-24), and plugins are self-contained (no `../` paths to other
repos; core is a declared dependency in `plugin.json`, never a file
dependency).

## Layout

```
your-plugin/
├── .claude-plugin/plugin.json    # name, version, description, dependencies, license
├── .github/workflows/plugin-gate.yml  # the merge gate below, as CI; rename the tag pattern
├── README.md · LICENSE · CITATION.cff
├── CONNECTORS.md                 # network disclosure; shared text + per-plugin table
├── skills/
│   └── example-workflow/SKILL.md # annotated example; replace it
├── agents/                       # subagents, one directory each
│   ├── example-scout/agent.md    # read-only planner skeleton; replace it
│   └── example-reviewer/agent.md # propose-never-modify auditor skeleton; replace it
├── knowledge/                    # OKF bundle (start from knowledge-template)
│   └── index.md · log.md
├── verification/                 # marimo golden notebooks
│   ├── example_workflow.py       # trivial green notebook; the pattern to copy
│   └── fixtures/                 # small fixed inputs + provenance README
└── evals/                        # eval cases, added with your gotchas
    └── SCHEMA.md                 # pointer to the case schema's one home
```

What the non-obvious files are for:

- `CONNECTORS.md` discloses what the plugin reaches over the network.
  The text above its "Registered servers" section is shared across the
  org and stays as written; the table under it is the per-plugin part.
  Facts about a service (endpoint, transport, tool surface, auth
  boundary) live in a `connector` concept in the bundle, and the table
  only summarizes them. A plugin with no `.mcp.json` says so in the
  table's place.
- `agents/<name>/agent.md` is the subagent shape: frontmatter `name`,
  `description`, `tools`; then Input, Behavior, Output and Must NOT for
  a planner, or Knowledge first, Input, Checks in order and Must NOT for
  a reviewer. Both skeletons consult the bundle through the core skill
  `consult-knowledge` by name rather than restating how; a reviewer
  proposes and never modifies. Placeholders are in angle brackets.
- `dependencies` in `plugin.json` is how a plugin reaches knowledge it
  does not own. Every plugin declares `core`; a plugin that consults a
  provider bundle (the PO.DAAC bundle in nasa-daac-knowledge, for
  example) adds that repository with a version floor,
  `{ "name": "nasa-daac-knowledge", "version": ">=2026.9.2" }`, and
  the installer installs and updates it alongside the plugin. Nothing
  is copied: skills and agents cite a provider concept by bundle path
  (`knowledge/podaac/<type>/<concept>.md`) and the core skill
  `consult-knowledge` finds every installed bundle through the
  installer's record. `knowledge/index.md` names each declared bundle
  under its own heading (the specification's canonical-home rule:
  the provider concept wins on conflict, `stable` outranks `draft`).
- `evals/SCHEMA.md` is a pointer, not a schema: the case format is
  documented once in marketplace/docs/eval-authoring-guide.md.

## The rules that gate a merge

`.github/workflows/plugin-gate.yml` runs rules 1, 3 (the PEP 723
header check), 4, the wording check (specification rules cited by
name, no program bookkeeping, no em or en dashes) and the
signature-debt measure on every pull request and on main, and enforces zero debt on a release tag; a plugin copied
from this template is gated from its first pull request. The one edit
it needs is the tag pattern, `{plugin-name}--v*`.

1. Every SKILL.md starts with frontmatter: `name`; `description` 200
   characters or fewer, keyword-first (verify the loaded budget with
   the /skills panel on Claude Code). Knowledge skills set
   `user-invocable: false`; workflow skills never set
   `disable-model-invocation: true` (it would kill conversational surfaces).
2. Side effects (downloads, file writes) are guarded by in-skill
   confirmation gates, in the skill body, so they work on every surface.
3. A workflow skill that encodes a computation is not done until its golden
   notebook in `verification/` runs green headless
   (`python verification/your_workflow.py`, nonzero exit on failure).
4. Knowledge bundles conform to the specification's knowledge-layer
   rules (docs/SPECIFICATION.md in open-science-pillars/marketplace);
   start from knowledge-template, which documents the frontmatter and
   the evidence rules.
5. Every high-severity gotcha ships a matching eval case in `evals/`.
