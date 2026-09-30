# Sanitized SusNet behavioral references

This directory is the only live-system-derived evidence available to ordinary
development agents. The committed examples are synthetic and contain no
operator information.

## Preparing a snapshot

An owner creates a temporary directory outside the repository with only these
optional files:

- `packages.txt`: one `package<TAB>version` pair per line.
- `services.txt`: one `service<TAB>active-state<TAB>sub-state` row per line.
- `usb.txt`: output limited to USB inventory lines.
- `alsa.txt`: output limited to playback/capture device inventory.
- `config-structure.json`: object whose keys are approved component names and
  whose values contain only section and field names, never values.

Run:

```sh
python3 tools/reference_collector.py \
  --source /path/to/raw-snapshot \
  --output /tmp/susnet-reference
python3 tools/security_scan.py --repository /tmp/susnet-reference
```

Review every generated file. Move the reviewed output into `reference/`, update
the provenance in `manifest.yaml`, then run `make sign-reference` with
`REFERENCE_SIGNING_KEY` pointing to a maintainer SSH signing key. Do not commit
the raw snapshot or signing key.

## Signature status

The initial manifest is intentionally marked `development-unsigned` because no
maintainer public key has been supplied. It is suitable for testing the
bootstrap, not as evidence for a qualification decision. The qualification
spike remains blocked until an owner reviews and signs a real sanitized
snapshot.
