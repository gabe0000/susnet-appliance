#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

from paths import BOOTSTRAP_FILES, ROOT


def main() -> int:
    missing = [path.relative_to(ROOT) for path in BOOTSTRAP_FILES if not path.is_file()]
    if missing:
        for path in missing:
            print(f"missing bootstrap file: {path}", file=sys.stderr)
        return 1

    for relative in ("build", "evidence/runs", ".susnet-lab"):
        path = ROOT / relative
        path.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(path, 0o700)
        except OSError:
            pass

    print("SusNet developer workspace initialized.")
    print("Next: make doctor && make test")
    print("The susnet-lab MCP server remains disabled.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
