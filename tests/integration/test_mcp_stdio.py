from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SERVER = ROOT / "tools/susnet_lab_mcp/server.py"


class MCPStdioTests(unittest.TestCase):
    def run_messages(self, messages):
        with tempfile.TemporaryDirectory() as state:
            environment = {**os.environ, "SUSNET_LAB_BACKEND": "fixture", "SUSNET_LAB_STATE_DIR": state}
            completed = subprocess.run(
                [sys.executable, str(SERVER)],
                input="".join(json.dumps(item) + "\n" for item in messages),
                text=True,
                capture_output=True,
                env=environment,
                timeout=10,
                check=True,
            )
            return [json.loads(line) for line in completed.stdout.splitlines()]

    def test_initialize_list_read_and_blocked_mutation(self):
        responses = self.run_messages(
            [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
                {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_lab_identity", "arguments": {}}},
                {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "reboot_test_pi", "arguments": {"reason": "qualification"}}},
            ]
        )
        self.assertEqual(responses[0]["result"]["serverInfo"]["name"], "susnet-lab")
        self.assertEqual(len(responses[1]["result"]["tools"]), 12)
        self.assertTrue(responses[2]["result"]["structuredContent"]["rf_inhibited"])
        self.assertEqual(responses[3]["result"]["structuredContent"]["state"], "blocked")

    def test_malformed_identifier_is_an_error_without_server_escape(self):
        response = self.run_messages(
            [{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_test_evidence", "arguments": {"run_id": "../../escape"}}}]
        )[0]
        self.assertEqual(response["error"]["code"], -32600)


if __name__ == "__main__":
    unittest.main()
