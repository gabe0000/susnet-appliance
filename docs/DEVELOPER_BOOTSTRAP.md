# SusNet developer bootstrap

This repository contains the agent contract and lab tooling for the standalone
SusNet Raspberry Pi appliance. It does not authorize access to the working
SusNet node or any CommsLab system.

## First session

1. Use Python 3.11 or newer, GNU Make, Git, OpenSSH, and Docker with Buildx.
   The supplied development container pins Python 3.12 on Debian Bookworm by
   OCI digest.
2. Trust the repository only after reviewing `AGENTS.md` and
   `.codex/config.toml`. The lab MCP server is present but disabled.
3. Run `make bootstrap`, then `make doctor`.
4. Read `docs/susnet-appliance/PLAN.md` and
   `docs/IMPLEMENTATION_STATUS.yaml`.
5. Work on the first unblocked milestone in a dedicated branch or worktree.
6. Run `make lint unit integration` before handoff.

Suggested agent prompt:

> Read `AGENTS.md`, the SusNet appliance `PLAN.md`, and
> `docs/IMPLEMENTATION_STATUS.yaml`. Run `make doctor`, identify the first
> unblocked milestone, and produce a short implementation checklist before
> editing. Use sanitized fixtures for reference. Do not access live SusNet,
> CommsLab, web01, or allstar01. Do not enable the lab MCP server until the
> milestone explicitly requires hardware qualification.

## Build environments

Ordinary editing, tests, fixture validation, and package-source work run in the
development container. Full image assembly requires a disposable, privileged,
native ARM64 Debian builder because the image workflow mounts filesystems and
uses Raspberry Pi ARM64 packages. The builder must not hold operator
credentials or deployment keys.

The `packages` and `image` make targets are release gates. They intentionally
remain blocked until their corresponding implementation milestones have the
required locked inputs and builder scripts. `make verify-image IMAGE=...`
performs safe artifact checks whenever a candidate image is available.

## Sanitized evidence

Agents use only `reference/`. An owner may prepare a raw snapshot locally and
pass it through `tools/reference_collector.py`; the collector never initiates a
network connection. Review the resulting manifest, scan it, and sign it with a
maintainer SSH signing key before treating it as evidence.

Raw snapshots and signing keys remain outside the repository. See
`reference/README.md` for the accepted input format.

## Lab MCP activation

Do not enable MCP until a dedicated disposable Pi is available. Provision the
root helper from `tools/susnet_lab_mcp/lab_helper.py`, its fixed action scripts,
a restricted `susnet-lab` account, and a host key in a dedicated known-hosts
file. Configure these local environment variables:

- `SUSNET_LAB_HOST`: DNS name beginning with `susnet-lab-`.
- `SUSNET_LAB_USER`: restricted account; defaults to `susnet-lab`.
- `SUSNET_LAB_EXPECTED_ID`: exact identity returned by the lab helper.
- `SUSNET_LAB_KNOWN_HOSTS`: private path to a pinned known-hosts file.
- `SUSNET_LAB_IDENTITY_FILE`: optional private SSH key path.

Then set `enabled = true` only in the developer's local Codex configuration or
in a temporary reviewed project override. The committed configuration remains
disabled. Confirm the server and tool list with `/mcp` or `codex mcp list`.

The MCP server refuses protected hostnames, verifies the remote lab identity
before mutations, accepts no model-supplied path or URL, and records an audit
event under `.susnet-lab/`. RF tests and firmware flashing additionally require
a short-lived physical authorization created on the Pi console.

## Reference documentation

- [Codex AGENTS.md guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Codex project configuration](https://learn.chatgpt.com/docs/config-file/config-basic)
- [Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp)
