# plugin-template

The scaffold for new Open Science Pillars domain plugins. Copy it, rename,
and replace the examples. Skills-only structure: there is NO `commands/`
directory anywhere in this org (everything is a skill; skills unification
of 2026-01-24), and plugins are self-contained (no `../` paths to other
repos; core is a peer install, never a file dependency).

## Layout

```
your-plugin/
├── .claude-plugin/plugin.json    # name, version, description, license
├── README.md · LICENSE · CITATION.cff
├── CONNECTORS.md                 # network disclosure (SPEC §5.9); shared text + per-plugin table
├── skills/
│   └── example-workflow/SKILL.md # annotated example; replace it
├── agents/                       # subagents, one directory each (SPEC §4.5)
│   ├── example-scout/agent.md    # read-only planner skeleton; replace it
│   └── example-reviewer/agent.md # propose-never-modify auditor skeleton; replace it
├── knowledge/                    # OKF bundle (start from knowledge-template)
│   ├── index.md · log.md
│   └── snapshot.yaml.example     # manifest for a pinned provider copy (SPEC §5.7)
├── verification/                 # marimo golden notebooks (SPEC §6)
│   ├── example_workflow.py       # trivial green notebook; the pattern to copy
│   └── fixtures/                 # small fixed inputs + provenance README
└── evals/                        # eval cases (SPEC §8), added with your gotchas
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
- `knowledge/snapshot.yaml.example` is the manifest a plugin fills in
  when it ships a pinned copy of another repository's concepts: rename
  it to `snapshot.yaml`, and the canonical repository's `sync_check.py`
  verifies and refreshes the copy against the pinned commit. A plugin
  whose bundle is original deletes the example and keeps no manifest;
  the `Snapshot source` lines in `index.md` then stay at "(none;
  original bundle)".
- `evals/SCHEMA.md` is a pointer, not a schema: the case format is
  documented once in marketplace/docs/eval-authoring-guide.md.

## The rules that gate a merge

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
4. Knowledge bundles conform to SPEC §5; start from knowledge-template,
   which documents the frontmatter and the evidence rules.
5. Every high-severity gotcha ships a matching eval case in `evals/`.
