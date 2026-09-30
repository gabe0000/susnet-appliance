#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
import tomllib
from html.parser import HTMLParser
from pathlib import Path

from paths import BOOTSTRAP_FILES, ROOT


class TemplateParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.labels: set[str] = set()
        self.inputs: set[str] = set()
        self.h1 = 0
        self.skip = False
        self.live = False
        self.external = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            self.ids.add(values["id"])
        if tag == "label" and "for" in values:
            self.labels.add(values["for"])
        if tag in {"input", "select", "textarea"} and "id" in values:
            self.inputs.add(values["id"])
        if tag == "h1":
            self.h1 += 1
        if tag == "a" and values.get("class") == "skip-link":
            self.skip = True
        if values.get("aria-live"):
            self.live = True
        for key in ("src", "href"):
            value = values.get(key, "")
            if value.startswith(("http://", "https://", "//")):
                self.external.append(value)


def parse_manifest(text: str) -> list[tuple[str, str]]:
    pairs = []
    path = None
    for line in text.splitlines():
        match_path = re.match(r"\s+- path: (.+)$", line)
        if match_path:
            path = match_path.group(1).strip()
            continue
        match_hash = re.match(r"\s+sha256: (.+)$", line)
        if match_hash and path:
            pairs.append((path, match_hash.group(1).strip()))
            path = None
    return pairs


def main() -> int:
    errors: list[str] = []
    for path in BOOTSTRAP_FILES:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")

    config_path = ROOT / ".codex" / "config.toml"
    if config_path.exists():
        with config_path.open("rb") as handle:
            config = tomllib.load(handle)
        server = config.get("mcp_servers", {}).get("susnet-lab", {})
        if server.get("enabled") is not False:
            errors.append("susnet-lab MCP must be disabled by default")
        if server.get("default_tools_approval_mode") != "writes":
            errors.append("susnet-lab write tools must require approval")

    template = ROOT / "templates" / "ui" / "index.html"
    if template.exists():
        parser = TemplateParser()
        parser.feed(template.read_text(encoding="utf-8"))
        if parser.h1 != 1:
            errors.append("UI template must contain exactly one h1")
        if not parser.skip or not parser.live:
            errors.append("UI template needs skip-link and aria-live status")
        if parser.inputs - parser.labels:
            errors.append(f"unlabeled fields: {sorted(parser.inputs - parser.labels)}")
        if parser.external:
            errors.append(f"external UI assets are prohibited: {parser.external}")

    manifest = ROOT / "reference" / "manifest.yaml"
    if manifest.exists():
        for relative, expected in parse_manifest(manifest.read_text(encoding="utf-8")):
            target = ROOT / "reference" / relative
            if not target.is_file():
                errors.append(f"missing reference file {relative}")
                continue
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
            if expected != actual:
                errors.append(f"reference hash mismatch for {relative}: expected {expected}, got {actual}")

    for json_path in (ROOT / "reference" / "fixtures").rglob("*.json"):
        try:
            json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON {json_path.relative_to(ROOT)}: {exc}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("SusNet bootstrap configuration, UI, and reference validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
