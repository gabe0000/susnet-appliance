#!/usr/bin/env python3
"""Turn an owner-provided local snapshot into reviewed, sanitized fixtures.

The collector intentionally has no network code. Its input is a directory of
small JSON/JSONL files created by an owner-run allowlisted collection process.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from security_scan import scan_text


ALLOWED_FILES = {
    "system/packages.json",
    "system/services.json",
    "system/hardware.json",
    "system/config-structure.json",
    "aprs/messages.jsonl",
    "meshcore/messages.json",
    "tts/announcements.json",
}
FORBIDDEN_KEYS = re.compile(
    r"(?:password|passwd|secret|token|private[_-]?key|credential|callsign|node[_-]?(?:id|number))",
    re.IGNORECASE,
)


def inspect_json(value: object, trail: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_trail = f"{trail}.{key}"
            if FORBIDDEN_KEYS.search(str(key)):
                errors.append(f"forbidden field {child_trail}")
            errors.extend(inspect_json(child, child_trail))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(inspect_json(child, f"{trail}[{index}]"))
    return errors


def load_records(path: Path) -> list[object]:
    if path.suffix == ".jsonl":
        records = []
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{number}: {exc}") from exc
        return records
    return [json.loads(path.read_text(encoding="utf-8"))]


def collect(source: Path, output: Path) -> list[tuple[str, str]]:
    if source.resolve() == output.resolve() or output.resolve() in source.resolve().parents:
        raise ValueError("source and output must be separate directories")
    present = {
        path.relative_to(source).as_posix()
        for path in source.rglob("*")
        if path.is_file()
    }
    unknown = present - ALLOWED_FILES
    if unknown:
        raise ValueError(f"unapproved input files: {', '.join(sorted(unknown))}")
    if not present:
        raise ValueError("snapshot contains no approved files")

    checked: list[tuple[Path, str]] = []
    errors: list[str] = []
    for relative in sorted(present):
        path = source / relative
        if path.is_symlink() or path.stat().st_size > 1_000_000:
            errors.append(f"unsafe input {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        errors.extend(f"{relative}: {item}" for item in scan_text(text))
        for record in load_records(path):
            errors.extend(f"{relative}: {item}" for item in inspect_json(record))
        checked.append((path, relative))
    if errors:
        raise ValueError("\n".join(errors))

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, mode=0o700)
    hashes: list[tuple[str, str]] = []
    for path, relative in checked:
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        hashes.append((relative, hashlib.sha256(target.read_bytes()).hexdigest()))
    return hashes


def write_manifest(path: Path, hashes: list[tuple[str, str]], collected_at: str) -> None:
    lines = [
        "schema_version: 1",
        "collection:",
        "  collector: tools/reference_collector.py",
        "  collector_version: 1",
        f"  collected_at: {collected_at}",
        "  source: owner-reviewed-snapshot",
        "  review_status: pending-maintainer-signature",
        "signature:",
        "  status: development-unsigned",
        "  namespace: susnet-reference",
        "  detached_file: null",
        "policy:",
        "  contains_operator_credentials: false",
        "  contains_personal_callsigns: false",
        "  contains_personal_node_numbers: false",
        "  contains_private_addresses: false",
        "  contains_unreviewed_logs: false",
        "files:",
    ]
    for relative, digest in hashes:
        lines.extend((f"  - path: fixtures/{relative}", f"    sha256: {digest}"))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    try:
        hashes = collect(args.source, args.output)
        write_manifest(
            args.manifest,
            hashes,
            datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        )
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"collection rejected: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {len(hashes)} sanitized fixture files and {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
