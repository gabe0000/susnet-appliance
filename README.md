# SusNet appliance

SusNet is a planned Raspberry Pi 4B appliance that brings five amateur-radio
workflows into one locally managed system:

- **AllStar** for one operator-owned RF node and one private local bridge.
- **DVSwitch** for the qualified Analog_Bridge, MMDVM_Bridge, and software
  vocoder path.
- **APRS** for APRS-IS receive, messaging, dashboard data, and optional
  announcements.
- **MeshCore** for a Heltec V3 USB companion using the US profile.
- **TTS** for explicit, bounded announcements from approved sources.

This repository currently contains the implementation plan, developer
bootstrap, synthetic fixtures, UI starter, and a disabled-by-default lab MCP
server. It does not yet contain a qualified appliance image. See
[`docs/IMPLEMENTATION_STATUS.yaml`](docs/IMPLEMENTATION_STATUS.yaml) for the
current release gate.

## Start developing

```sh
make bootstrap
make doctor
make test
```

Read [`AGENTS.md`](AGENTS.md), the
[`implementation plan`](docs/susnet-appliance/PLAN.md), and the
[`developer handoff`](docs/HANDOFF.md) before editing. All fixtures use
fabricated identities. The committed Codex MCP configuration is disabled.

The appliance's plain-language account checklist is in
[`docs/USER_CREDENTIALS.md`](docs/USER_CREDENTIALS.md). It links operators to
official registration and credential instructions for every optional network.

## Safety and privacy

Do not place passwords, access tokens, private keys, real callsigns, node
numbers, personalized configurations, or unreviewed logs in this repository.
Live SusNet, CommsLab, web01, and allstar01 are outside the project boundary.
RF transmission remains inhibited until its hardware acceptance gate passes.

## Project status

The next gate is the hardware qualification spike. It must identify the exact
AURSINC revision and wiring, freeze the Heltec V3 firmware/profile, and prove
the ARM64 DVSwitch software-vocoder path before image implementation begins.

Licensed under the [MIT License](LICENSE).
