# plugin-template

The scaffold for a new Open Science Pillars capability: copy it, rename
it, replace the examples, and the gate runs on your first pull request.
The walkthrough with measured timings is
[Tutorial 3, Build a Domain Plugin](https://github.com/open-science-pillars/tutorials/blob/main/tutorial-3-build-a-plugin.qmd)
in the tutorials repository (12.3 minutes scaffold-to-installed); what
every file under `.osp/` means, and how a dependency, a connector or a
PROVE requirement is declared, is the marketplace repository's
[package authoring guide](https://github.com/open-science-pillars/marketplace/blob/main/docs/package-authoring-guide.md).
The words used on this page (capability, plugin, package, sphere,
knowledge bundle, runtime) are defined in the
[glossary](https://github.com/open-science-pillars/marketplace/blob/main/GLOSSARY.md).

## From copy to gated

1. **Copy the repository.** Create the new repository from this one (a
   template copy or a clone with the history dropped) in a workspace
   that also holds a checkout of
   [build-kit](https://github.com/open-science-pillars/build-kit) and
   [nasa-daac-knowledge](https://github.com/open-science-pillars/nasa-daac-knowledge)
   beside it, the way the gate lays them out.
2. **Rename.** Set `repository.name` in `.osp/repository.yaml` (a copy
   fails `osp.py validate` until it is no longer `plugin-template`) and,
   for a domain capability, set `kind` to `capability` there with its
   sphere and discipline; set the package
   `name`, `description` and `keywords` in `.osp/package.yaml`; rename
   the release tag pattern in `.github/workflows/plugin-gate.yml` to
   `<plugin-name>--v*`; and put the plugin's name at the top of
   `CONNECTORS.md`.
3. **Delete the examples** once you have real ones: the example skill
   with its helper script (`skills/example-workflow/`, including
   `scripts/example_helper.py`), the two example agents
   (`agents/example-scout/`, `agents/example-reviewer/`), the example
   golden notebook (`verification/example_workflow.py`) and its fixture
   (`verification/fixtures/example_series.csv` with the
   `make_fixtures.py` that writes it; keep the fixtures README and
   record your own fixtures in it). The knowledge
   bundle starts empty (its concepts come from
   [knowledge-template](https://github.com/open-science-pillars/knowledge-template))
   and `evals/` holds only the pointer to the case schema; the first
   high-severity gotcha you write brings the first eval case with it.
4. **Validate and render.** From the repository root:
   `uv run ../build-kit/scripts/osp.py validate . && uv run ../build-kit/scripts/osp.py render .`
   The second command writes the Claude manifest and `.mcp.json` and
   the Agent Plugins `plugin.json` and `mcp.json` from
   `.osp/package.yaml`; never edit those four by hand, the gate fails
   on a hand edit.
5. **Open the first pull request.** `.github/workflows/plugin-gate.yml`
   runs on every pull request and on main: the manifest validates
   (`claude plugin validate`), the canonical metadata validates and the
   projections are current (`osp.py validate`, `osp.py render --check`),
   the portable package conforms to Agent Plugins 1.0.0
   (`osp.py plugin-check`), every file of code has one home by plane
   (`osp.py placement-check`, the placement rule of ADR C), the
   README's runtime table is current and no
   runtime is advertised without a qualified record (`osp.py advertise
   --check`), the release lock is reported, the bundle conforms to OKF
   v0.2 (`check_okf_v02.py`), every script's PEP 723 header covers what
   it imports (`check_script_deps.py`), the wording rules hold
   (`check_prose.py`: specification rules cited by name, no program
   bookkeeping, no em or en dashes) and the signature debt is reported
   (`signature_check.py`); a release tag enforces the lock and zero
   debt. `.github/workflows/goldens.yml` runs every golden notebook at
   the top of `verification/` headless on the committed fixtures.
   `.github/workflows/release-qualification.yml` treats a pull
   request that changes the package version, or carries the `release`
   label, as a release candidate: one ticket opens per required runtime
   and the merge waits on a qualification record or a waiver for each
   (the marketplace repository's
   [release qualification guide](https://github.com/open-science-pillars/marketplace/blob/main/docs/release-qualification-guide.md)).

## Layout

```
your-plugin/
├── .claude-plugin/plugin.json    # the Claude projection, rendered from .osp/package.yaml
├── .mcp.json                     # the Claude connector wire, rendered likewise (when reach is declared)
├── plugin.json · mcp.json        # the Agent Plugins 1.0.0 projection, rendered likewise
├── .osp/                         # canonical metadata (the package authoring guide):
│   ├── repository.yaml           #   kind, status, spheres, discipline
│   ├── package.yaml              #   name, version, dependencies, metadata, reach
│   ├── release-lock.json         #   digests of one release, written by osp.py lock
│   ├── surfaces.yaml             #   runtime support policy and the qualification a release needs
│   └── governance.yaml           #   maintainers, runtime maintainers, review policy
├── .github/workflows/
│   ├── plugin-gate.yml           # the merge gate, as CI; rename the tag pattern
│   ├── goldens.yml               # every golden notebook, headless, on the committed fixtures
│   └── release-qualification.yml # tickets per required runtime on a release candidate
├── README.md · LICENSE · CITATION.cff
├── CONNECTORS.md                 # network disclosure; shared text plus the per-plugin table
├── skills/
│   └── example-workflow/         # annotated example; replace it
│       ├── SKILL.md              #   the procedure
│       └── scripts/              #   what the procedure runs at runtime, through the plugin root
│           └── example_helper.py #   PEP 723 header, --selftest
├── agents/                       # subagents, one directory each
│   ├── example-scout/agent.md    # read-only planner skeleton; replace it
│   └── example-reviewer/agent.md # propose-never-modify auditor skeleton; replace it
├── knowledge/                    # OKF bundle (start from knowledge-template)
│   └── index.md · log.md
├── verification/                 # marimo golden notebooks; nothing here is run by a skill
│   ├── example_workflow.py       # green notebook on the fixture; the pattern to copy
│   └── fixtures/                 # small fixed inputs plus the provenance README
│       ├── README.md             #   source, version and license of every fixture
│       ├── make_fixtures.py      #   the builder that writes the synthetic fixture
│       └── example_series.csv    #   the fixture the golden and the helper read
└── evals/                        # eval cases, added with your gotchas
    ├── README.md                 # what lives here and where the format is defined
    └── SCHEMA.md                 # pointer to the case schema's one home
```

## The rules that gate a merge

1. Every `SKILL.md` starts with frontmatter: `name`; `description` 200
   characters or fewer, keyword-first (verify the loaded budget with
   the skills panel on Claude Code). Knowledge skills set
   `user-invocable: false`; workflow skills never set
   `disable-model-invocation: true` (it would kill conversational
   runtimes).
2. Side effects (downloads, file writes) are guarded by in-skill
   confirmation gates, in the skill body, so they work on every runtime.
3. A workflow skill that encodes a computation is not done until its
   golden notebook in `verification/` runs green headless
   (`uv run verification/your_workflow.py`, nonzero exit on failure;
   the PEP 723 header at the top of the file is what makes that resolve
   on any machine). The notebook reads its inputs from
   `verification/fixtures/` and may import the skill's helper by path;
   the goldens workflow runs every notebook at the top of
   `verification/`.
4. Every file of code has one home by plane (the placement rule, ADR C
   in the marketplace repository's docs/decisions): sanctioned code a
   concept names stays in `knowledge/<bundle>/references/`, a procedure
   is a `SKILL.md`, a script a skill runs at runtime is in
   `skills/<name>/scripts/` and is invoked through
   `${CLAUDE_PLUGIN_ROOT}`, a golden and its fixtures are under
   `verification/` where no skill names them, and
   `osp.py placement-check` in the gate reports the row a file breaks.
5. Knowledge bundles conform to the specification's knowledge-layer
   rules (docs/SPECIFICATION.md in open-science-pillars/marketplace);
   start from knowledge-template, which carries an annotated example per
   concept type.
6. Every high-severity gotcha ships a matching eval case in `evals/`;
   the case format is the marketplace repository's
   [docs/testing.md](https://github.com/open-science-pillars/marketplace/blob/main/docs/testing.md).

The sections below are the README your capability ships. Keep their
order (it is the one every capability in the organization uses),
replace every `<placeholder>`, and leave the runtime table to the tool
that renders it.

# <plugin-name>

<One paragraph for a scientist, in plain words: what you can do with
this capability, with no organization vocabulary before a concrete
sentence.> It is a <Sphere> capability, discipline <Discipline>
(`kind: capability` in `.osp/repository.yaml`); the words used on this page
(capability, plugin, sphere, knowledge bundle, runtime) are defined in
the
[glossary](https://github.com/open-science-pillars/marketplace/blob/main/GLOSSARY.md).

## Install

On Claude Code:

```bash
claude plugin marketplace add open-science-pillars/marketplace
claude plugin install <plugin-name>@open-science-pillars
```

What comes with it: `core` <and any knowledge dependency, by name>,
declared as dependencies, so the one install brings them with it. An
install stays at the release it was installed from:
`claude plugin update <plugin-name>@open-science-pillars` moves this
plugin and only this plugin; a dependency moves by its own update
command, and a release that raises a floor says so in its notes.
`claude plugin list` shows what you have.

On Claude Cowork: add the marketplace by repository
(`open-science-pillars/marketplace`) under Customize > Plugins > Add
marketplace, then install the same capability from it; the shell
commands on this page are for Claude Code.

Local requirements: [uv](https://docs.astral.sh/uv/getting-started/installation/).
Every script here declares its dependencies in a PEP 723 header and runs
as `uv run <script>`; never `python script.py`. <Which credential
retrieval needs (an Earthdata Login, a service key), which archives need
a further authorization on the account, and that searching needs none.>

## Runtimes

Which runtimes this release is qualified on is the table below, rendered
from the qualification records; what each word asserts is in the
marketplace repository's
[docs/runtime-distribution.md](https://github.com/open-science-pillars/marketplace/blob/main/docs/runtime-distribution.md).

<!-- osp-runtimes:start -->
Runtime support for your-plugin-name 0.1.0 (release lock `sha256:d579855e2d22`), rendered by build-kit's `osp.py advertise` from `.osp/surfaces.yaml` and the qualification records; edit those, not this block.

| Runtime | Role | Declared status | Qualification |
|---|---|---|---|
| Claude Code | development and runtime, required | supported | Supported (development environment) |
| Claude Cowork | runtime, required | planned | Not qualified |
| OpenAI Codex | runtime, required | planned | Not qualified |
| Claude Science | future runtime | limited-release | Outside the required matrix |

A runtime is advertised as supported only on a qualified record for this exact release; a release stays valid when a runtime is not qualified, and that runtime is simply not advertised.
<!-- osp-runtimes:end -->

## First result

<Link `tutorials/quickstart.md` in this repository, with its measured
time and what it assumes; then the timed tutorial in the tutorials
repository for the long form.>

## What's inside

- **Skills** (`skills/`, one `SKILL.md` each, runtime helpers in its
  `scripts/`): <names, two or three lines>.
- **Agents** (`agents/`): <names and what each proposes>.
- **Knowledge** (`knowledge/`): <what the local bundle holds, and the
  provider bundle it depends on, by repository and bundle path>.
- **Verification** (`verification/`): <the golden notebooks by name>.
- **Evals** (`evals/`): <the cases, or the repository that is their
  home>.

## Configuration

<The `<plugin-name>.local.md.template` file, where to copy it, what it
controls; omit the section if the capability has no local file.>

## Connectors and credentials

<Two lines: what the connectors reach and which credential is read
where.> The disclosure is [CONNECTORS.md](CONNECTORS.md).

## Contributing

Start with the marketplace repository's
[CONTRIBUTING.md](https://github.com/open-science-pillars/marketplace/blob/main/CONTRIBUTING.md)
and the guides under its `docs/` (contributing a skill, contributing
knowledge, testing, the package authoring guide).

## License and citation

Apache-2.0. Cite via [CITATION.cff](CITATION.cff).
