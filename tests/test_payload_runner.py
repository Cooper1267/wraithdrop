import unittest
from utils.payload_runner import PayloadRunner

class TestPayloadRunner(unittest.TestCase):
    def setUp(self):
        self.runner = PayloadRunner(dry_run=True)

    def test_simulate_whoami(self):
        result = self.runner.simulate_whoami()
        self.assertEqual(result["returncode"], 0)

    def test_simulate_netstat(self):
        result = self.runner.simulate_netstat()
        self.assertEqual(result["returncode"], 0)

    def test_simulate_reg_query_non_windows(self):
        if self.runner.os != "windows":
            result = self.runner.simulate_reg_query()
            self.assertNotEqual(result["returncode"], 0)
            self.assertIn("not supported", result["error"])

    def test_run_invalid_command(self):
        result = self.runner.run("nonexistentcommand1234")
        self.assertNotEqual(result["returncode"], 0)

if __name__ == "__main__":
    unittest.main()

