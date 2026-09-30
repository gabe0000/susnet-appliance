from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from release_gate import milestone_status


class ReleaseGateTests(unittest.TestCase):
    def test_reads_only_requested_milestone(self):
        text = "milestones:\n  - id: one\n    status: complete\n  - id: two\n    status: blocked\n"
        self.assertEqual(milestone_status(text, "one"), "complete")
        self.assertEqual(milestone_status(text, "two"), "blocked")
        self.assertIsNone(milestone_status(text, "three"))


if __name__ == "__main__":
    unittest.main()
