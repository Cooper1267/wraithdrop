import unittest
from modules.recon import basic_fingerprint

class TestBasicFingerprint(unittest.TestCase):
    def test_run_returns_expected_keys(self):
        result = basic_fingerprint.run(dry_run=True)
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("module"), "basic_fingerprint")
        self.assertIn("payloads_executed", result)
        self.assertIn("results", result)
        for cmd in result["payloads_executed"]:
            self.assertIn(cmd, result["results"])
            self.assertIn("output", result["results"][cmd])
            self.assertIn("success", result["results"][cmd])

if __name__ == "__main__":
    unittest.main()

       
