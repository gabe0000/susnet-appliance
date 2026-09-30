#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import shutil
import tarfile
import tempfile
from pathlib import Path

from paths import ROOT
from security_scan import iter_files, scan_text


FILES = (
    ".gitignore",
    "AGENTS.md",
    "LICENSE",
    "Makefile",
    "README.md",
    "pyproject.toml",
    ".codex/config.toml",
    ".devcontainer/devcontainer.json",
    "docs/COMPONENT_SCOPE.md",
    "docs/DECISIONS.md",
    "docs/DEVELOPER_BOOTSTRAP.md",
    "docs/HANDOFF.md",
    "docs/IMPLEMENTATION_STATUS.yaml",
    "docs/UI_STYLE_GUIDE.md",
    "docs/USER_CREDENTIALS.md",
)
TREES = ("docs/susnet-appliance", "reference", "templates", "tools", "tests")


def copy_public_tree(destination: Path) -> None:
    for relative in FILES:
        source = ROOT / relative
        if not source.is_file():
            raise FileNotFoundError(relative)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for relative in TREES:
        source = ROOT / relative
        if not source.is_dir():
            raise FileNotFoundError(relative)
        shutil.copytree(source, destination / relative, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def validate_public_tree(root: Path) -> list[Path]:
    findings = []
    files = sorted(iter_files(root))
    for path in files:
        if path.is_symlink():
            findings.append(f"symlink prohibited: {path.relative_to(root)}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"binary file prohibited: {path.relative_to(root)}")
            continue
        for issue in scan_text(text):
            findings.append(f"{path.relative_to(root)}: {issue}")
    if findings:
        raise ValueError("public tree rejected:\n" + "\n".join(findings))
    return files


def write_sums(root: Path, files: list[Path]) -> None:
    lines = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {relative}")
    (root / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--directory", type=Path, help="also write the clean public tree here")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="susnet-handoff-") as temp:
        root = Path(temp) / "susnet-appliance"
        root.mkdir()
        copy_public_tree(root)
        files = validate_public_tree(root)
        write_sums(root, files)
        if args.directory:
            if args.directory.exists():
                shutil.rmtree(args.directory)
            shutil.copytree(root, args.directory)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(args.output, "w:gz", format=tarfile.PAX_FORMAT) as archive:
            archive.add(root, arcname="susnet-appliance", recursive=True)
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print(f"Wrote {args.output}\nSHA-256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
