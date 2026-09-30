#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1]:
        print("set IMAGE to a candidate .img or .img.xz file", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file() or not path.name.endswith((".img", ".img.xz")):
        print("candidate must be an existing .img or .img.xz file", file=sys.stderr)
        return 1
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    report = {"path": path.name, "bytes": path.stat().st_size, "sha256": digest, "inspection": "artifact-only"}
    print(json.dumps(report, indent=2))
    print("Filesystem and first-boot verification require the ARM64 image test runner.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
