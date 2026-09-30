# SusNet appliance repository guidance

Before changing SusNet appliance files, read `docs/susnet-appliance/PLAN.md`,
`docs/DEVELOPER_BOOTSTRAP.md`, and `docs/IMPLEMENTATION_STATUS.yaml`. Run
`make doctor`, then work only on the first unblocked milestone unless the task
explicitly names another one.

- Treat CommsLab, web01, allstar01, and live SusNet as protected, out-of-scope
  systems. Never connect to or change them from this repository.
- Use only sanitized files under `reference/` as behavioral evidence. Never
  import credentials, callsigns, node numbers, private addresses, unreviewed
  logs, or personalized configuration.
- Keep RF transmit paths inhibited until the applicable hardware acceptance
  gate is recorded as passed. Never bypass physical interlocks or approval
  tokens.
- The `susnet-lab` MCP server may target only a dedicated disposable test Pi.
  It stays disabled during ordinary development.
- Keep secrets out of source, command lines, logs, fixtures, tests, and build
  artifacts. Use synthetic identifiers in every automated test.
- Preserve the official ASL3/Trixie base and the package, transaction,
  firewall, recovery, and scope boundaries in the plan.
- Keep the product surface focused on AllStar, DVSwitch, APRS, MeshCore, and
  TTS. Do not import unrelated experiments. MeshCore-to-TTS remains prohibited.
- Record durable design changes in `docs/DECISIONS.md` and update
  `docs/IMPLEMENTATION_STATUS.yaml` with evidence before handing work off.
- Run `make lint unit integration` for bootstrap changes. Run the additional
  package, image, or qualification targets required by the active milestone.

UI work must begin with `templates/ui/` and follow
`docs/UI_STYLE_GUIDE.md`. Do not add external fonts, scripts, analytics, or CDN
assets to the appliance interface.
