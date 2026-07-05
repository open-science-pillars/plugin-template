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
├── skills/
│   └── example-workflow/SKILL.md # annotated example; replace it
├── knowledge/                    # OKF bundle (start from knowledge-template)
│   ├── index.md · log.md
├── verification/                 # marimo golden notebooks (SPEC §6)
│   ├── example_workflow.py       # trivial green notebook; the pattern to copy
│   └── fixtures/                 # small fixed inputs + provenance README
└── evals/                        # eval cases (SPEC §8), added with your gotchas
```

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
