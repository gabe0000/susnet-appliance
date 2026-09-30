# SusNet developer handoff

This handoff captures SusNet at the planning and agent-bootstrap stage. It does
not contain a finished appliance image, operator credentials, live-system
configuration, or authorization to access existing infrastructure.

## What is ready

- Decision-complete appliance plan.
- Codex-compatible repository instructions and project settings.
- Reproducible developer command surface and pinned development container.
- Synthetic, sanitized behavioral fixtures and owner-side collection tooling.
- Framework-neutral UI styling starter for the wizard and dashboard.
- Disabled-by-default, constrained lab MCP server and test-Pi helper contract.
- Automated validation, security, MCP contract, and handoff-bundle tests.
- Explicit contracts and synthetic examples for AllStar, DVSwitch, APRS,
  MeshCore, and TTS.
- A plain-language user credential checklist with official account links and
  clear distinctions between website passwords and service credentials.

## Current engineering gate

Milestone `M1-qualification-spike` is next. It must identify the exact AURSINC
kit, freeze the Heltec V3 US profile, prove the software-only DMR path on
Trixie/ARM64, and resolve redistribution terms before image work begins. See
`docs/IMPLEMENTATION_STATUS.yaml` for the authoritative status.

## Start here

```sh
make bootstrap
make doctor
make test
```

Then give Codex the starting prompt in `docs/DEVELOPER_BOOTSTRAP.md`. The lab MCP
server remains disabled. Normal work uses `reference/` only.

## Boundaries

- Do not access live SusNet, CommsLab, web01, or allstar01.
- Do not insert a real callsign, node number, password, private key, or private
  network address into the repository.
- Do not enable RF transmission during development.
- Do not mark a release gate passed without attaching reviewable evidence.
- Do not distribute a pilot image until the full plan's acceptance gates pass.

## Clean transfer

Run `make handoff`. It creates `build/susnet-developer-handoff.tar.gz` from an
explicit SusNet-only allowlist, adds a hashed file manifest, and excludes the
unrelated infrastructure and experiments in this repository. The same clean
tree can be used to initialize the standalone public GitHub repository.
