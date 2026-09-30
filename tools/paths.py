from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

BOOTSTRAP_FILES = (
    ROOT / "README.md",
    ROOT / "LICENSE",
    ROOT / "AGENTS.md",
    ROOT / "Makefile",
    ROOT / "pyproject.toml",
    ROOT / ".codex" / "config.toml",
    ROOT / ".devcontainer" / "devcontainer.json",
    ROOT / "docs" / "DEVELOPER_BOOTSTRAP.md",
    ROOT / "docs" / "IMPLEMENTATION_STATUS.yaml",
    ROOT / "docs" / "DECISIONS.md",
    ROOT / "docs" / "HANDOFF.md",
    ROOT / "docs" / "UI_STYLE_GUIDE.md",
    ROOT / "docs" / "COMPONENT_SCOPE.md",
    ROOT / "docs" / "USER_CREDENTIALS.md",
    ROOT / "docs" / "susnet-appliance" / "PLAN.md",
    ROOT / "reference" / "manifest.yaml",
    ROOT / "templates" / "ui" / "index.html",
)

SUSNET_SCAN_ROOTS = (
    ROOT / "README.md",
    ROOT / "LICENSE",
    ROOT / "AGENTS.md",
    ROOT / "Makefile",
    ROOT / "pyproject.toml",
    ROOT / ".codex",
    ROOT / ".devcontainer",
    ROOT / "docs" / "DEVELOPER_BOOTSTRAP.md",
    ROOT / "docs" / "IMPLEMENTATION_STATUS.yaml",
    ROOT / "docs" / "DECISIONS.md",
    ROOT / "docs" / "HANDOFF.md",
    ROOT / "docs" / "UI_STYLE_GUIDE.md",
    ROOT / "docs" / "COMPONENT_SCOPE.md",
    ROOT / "docs" / "USER_CREDENTIALS.md",
    ROOT / "docs" / "susnet-appliance",
    ROOT / "reference",
    ROOT / "templates" / "ui",
    ROOT / "tools",
)
