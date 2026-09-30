# SusNet architecture decisions

This log is append-only. Correct a decision with a new entry that supersedes
the earlier one; do not rewrite history after implementation begins.

## ADR-0001 — Repository context before dynamic tools

- **Date:** 2026-09-29
- **Status:** accepted
- **Decision:** Keep durable project context in versioned repository files.
  Use MCP only for bounded lab observations and operations.
- **Reason:** Developers and agents must receive identical goals and safety
  boundaries without depending on a running service.
- **Rejected:** Using an MCP server as the primary store for plans and project
  instructions.

## ADR-0002 — Fixtures before lab access

- **Date:** 2026-09-29
- **Status:** accepted
- **Decision:** Normal development uses sanitized, signed fixtures. The lab MCP
  server is disabled until hardware qualification.
- **Reason:** This prevents incidental access to live SusNet and keeps tests
  deterministic.
- **Rejected:** Direct agent SSH access to the working node.

## ADR-0003 — Local STDIO MCP with fixed remote helper

- **Date:** 2026-09-29
- **Status:** accepted
- **Decision:** Run `susnet-lab` as a local STDIO MCP process. It connects with
  pinned SSH host identity to a dedicated test Pi and invokes only one fixed,
  structured helper.
- **Reason:** Local configuration is simple while remote permissions remain
  narrow and auditable.
- **Rejected:** A generic shell MCP server and a publicly reachable HTTP MCP
  endpoint.

## ADR-0004 — Appliance UI starter

- **Date:** 2026-09-29
- **Status:** accepted
- **Decision:** Use the local assets in `templates/ui/` as the visual and
  interaction baseline for the setup wizard and dashboard.
- **Reason:** The operator experience needs a consistent, accessible language
  without copying personalized live-SusNet pages or depending on a CDN.
- **Rejected:** Reusing the public web01 site directly or letting each feature
  invent its own controls.
