# Connectors: <your-plugin-name>

What this plugin talks to over the network, what leaves your machine
when it does, and what happens when it cannot. This file is the
disclosure; `.mcp.json` is the wire.

The sections up to "Registered servers" are shared text: they state the
connector rules every plugin in the org follows (the specification,
docs/SPECIFICATION.md in open-science-pillars/marketplace) and are
kept as they are. The per-plugin block at the end is where this
plugin's own servers are listed; a plugin that registers no server
keeps the shared text and says so there.

## What a connector is

A connector is the REACH plane only: the registration wire
(`.mcp.json`) that gives an agent an interactive path to an external
service. Three rules keep it in its plane.

**Connector facts live in the bundle.** Endpoint, transport, tool
surface, auth boundary and deprecation status are world-falsifiable
claims, so they are recorded as a `connector` concept with sources,
verification dates and a `stale_after` matched to the service's
announced flux, re-verified by a smoke run at each steward sweep; an
endpoint, transport or tool-surface change opens an issue before any
doc changes. This file deliberately does not restate them, so there is
one place to correct when they change.

**Gates never depend on connectors.** Verification tooling and
attesters call provider REST APIs directly, because deterministic
receipt-producing checks cannot inherit an interactive service's
availability or evolution.

**Discovery never outranks signed knowledge.** An interactive catalog
result may inform drafting and cross-checks, but a bundle claim (a
schema row, a ShortName, a caveat) changes only through the concept
lifecycle with its own verification.

## What leaves your machine

Query parameters only: names, identifiers, keywords and the spatial or
temporal bounds of a request, sent over HTTPS to the endpoint the
connector concept names. No file, no local path and no data you hold
passes through a connector. Downloads do not go through a connector:
retrieval happens directly between your machine and the archive
through the loading library, which is why an unreachable connector
cannot block a download.

## Credentials

A login is needed only where retrieval requires one, never to search.
It is read by the loading library at retrieval time and is never
handled by this plugin, never sent to a connector, and never stored in
this repository in any form.

## When a connector is unavailable

Nothing breaks. Gates and attesters never call a connector; discovery
falls back to the knowledge bundle with archive URLs and says out loud
which path it used; loading proceeds from local files or direct
library access.

## Per-surface

Claude Code and Cowork read `.mcp.json` from the installed plugin.
Claude Science configures connectors per session; see
marketplace/docs/surface-testing-guide.md.

## Registered servers (per plugin: fill in)

One row per server key in `.mcp.json`. Every fact in a row summarizes
the connector concept named in its last column; when a fact changes,
correct the concept first, then the row. A server run from a URL is
commit-pinned in `.mcp.json`; the pin moves only by a reviewed edit.

| Server (`.mcp.json` key) | Endpoint | Transport | Tool surface | Auth boundary | Connector concept |
|---|---|---|---|---|---|
| `<key>` | `<host or command>` | `<streamable-http, stdio, ...>` | `<what its tools do, in a phrase>` | `<anonymous, or which credential and where it stays>` | `<knowledge/connectors/<name>.md, or the provider bundle path>` |

For each server, add below the table only what the shared text does
not already say: what this plugin uses it for (which skills or agents,
which query groups) and any degradation detail specific to this plugin.

If this plugin registers no server, replace the table with: this
plugin registers no connector; every workflow runs on local files and
direct library access.
