from __future__ import annotations

import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class HandoffBundleTests(unittest.TestCase):
    def test_bundle_contains_only_allowlisted_project_tree(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp) / "handoff.tar.gz"
            subprocess.run(
                [sys.executable, str(ROOT / "tools/handoff_bundle.py"), "--output", str(archive)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            with tarfile.open(archive) as handle:
                names = set(handle.getnames())
            self.assertIn("susnet-appliance/README.md", names)
            self.assertIn("susnet-appliance/docs/USER_CREDENTIALS.md", names)
            self.assertIn("susnet-appliance/SHA256SUMS", names)
            self.assertFalse(any("web01" in name or "stacks/web-landing" in name for name in names))


if __name__ == "__main__":
    unittest.main()
