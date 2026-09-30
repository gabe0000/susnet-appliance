from __future__ import annotations

import sys
import unittest
from pathlib import Path


MODULE = Path(__file__).resolve().parents[2] / "tools" / "susnet_lab_mcp"
sys.path.insert(0, str(MODULE))

from contracts import ALL_TOOLS, READ_TOOLS, TOOLS, WRITE_TOOLS, validate_arguments


class ContractTests(unittest.TestCase):
    def test_expected_tool_partition(self):
        self.assertEqual(set(TOOLS), ALL_TOOLS)
        self.assertFalse(READ_TOOLS & WRITE_TOOLS)
        self.assertEqual(len(ALL_TOOLS), 12)

    def test_unknown_fields_and_path_like_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_arguments("get_lab_identity", {"path": "/etc/shadow"})
        with self.assertRaises(ValueError):
            validate_arguments("get_test_evidence", {"run_id": "../../escape"})

    def test_arbitrary_service_and_url_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_arguments("get_sanitized_logs", {"service": "ssh"})
        with self.assertRaises(ValueError):
            validate_arguments("install_candidate", {"build_id": "https://example.invalid/a", "sha256": "0" * 64})

    def test_rf_timeout_and_token_are_bounded(self):
        valid = validate_arguments(
            "run_guarded_rf_test",
            {"test": "dummy-load-audio", "physical_token": "ABCDEFGH", "max_seconds": 10},
        )
        self.assertEqual(valid["max_seconds"], 10)
        with self.assertRaises(ValueError):
            validate_arguments(
                "run_guarded_rf_test",
                {"test": "dummy-load-audio", "physical_token": "ABCDEFGH", "max_seconds": 11},
            )


if __name__ == "__main__":
    unittest.main()
