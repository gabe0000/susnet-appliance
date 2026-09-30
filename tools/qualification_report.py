#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records = []
    if args.evidence.exists():
        for path in sorted(args.evidence.glob("*.json")):
            records.append((path, json.loads(path.read_text(encoding="utf-8"))))
    lines = [
        "# SusNet qualification report",
        "",
        "> Generated from structured lab evidence. No run is a release approval by itself.",
        "",
        f"Evidence records: **{len(records)}**",
        "",
    ]
    for path, record in records:
        lines.extend(
            [
                f"## {record.get('run_id', path.stem)}",
                "",
                f"- State: `{record.get('state', 'unknown')}`",
                f"- Test: `{record.get('test', 'unknown')}`",
                f"- Image hash: `{record.get('image_sha256', 'not-recorded')}`",
                f"- Evidence file: `{path.name}`",
                f"- Evidence SHA-256: `{hashlib.sha256(path.read_bytes()).hexdigest()}`",
                "",
            ]
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
