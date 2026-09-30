#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

from paths import ROOT


def update_hashes(manifest: Path) -> int:
    lines = manifest.read_text(encoding="utf-8").splitlines()
    path: str | None = None
    count = 0
    for index, line in enumerate(lines):
        match = re.match(r"\s+- path: (.+)$", line)
        if match:
            path = match.group(1).strip()
            continue
        if path and re.match(r"\s+sha256:", line):
            fixture = manifest.parent / path
            if not fixture.is_file():
                raise FileNotFoundError(fixture)
            lines[index] = f"    sha256: {hashlib.sha256(fixture.read_bytes()).hexdigest()}"
            count += 1
            path = None
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=ROOT / "reference/manifest.yaml")
    parser.add_argument("--key", help="SSH signing key path; omit to refresh hashes only")
    args = parser.parse_args()
    try:
        count = update_hashes(args.manifest)
        if args.key:
            signature = args.manifest.with_suffix(args.manifest.suffix + ".sig")
            subprocess.run(
                ["ssh-keygen", "-Y", "sign", "-f", args.key, "-n", "susnet-reference", str(args.manifest)],
                check=True,
            )
            generated = Path(str(args.manifest) + ".sig")
            if generated != signature:
                generated.replace(signature)
        print(f"Updated {count} reference hashes" + (" and wrote detached signature" if args.key else ""))
        return 0
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"reference signing failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
