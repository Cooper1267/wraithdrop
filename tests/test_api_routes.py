import unittest
import json
from wraithdrop_main import create_app

VALID_TOKEN = "mysecrettoken"  # Must match the token expected in auth.py

class APIRouteTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True).test_client()
        self.headers = {
            "Authorization": f"Bearer {VALID_TOKEN}",
            "Content-Type": "application/json"
        }

    def test_status_endpoint(self):
        res = self.app.get('/api/status', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertIn("status", res.get_json())

    def test_logs_endpoint(self):
        res = self.app.get('/api/logs', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.get_json(), list)

    def test_run_endpoint_authorized(self):
        data = {"ttp": "profiles/apt29.yaml"}
        res = self.app.post('/api/run', headers=self.headers, data=json.dumps(data))
        self.assertIn(res.status_code, [200, 202])  # Depends on profile structure

    def test_validate_endpoint(self):
        fake_profile = {
            "name": "TestChain",
            "steps": ["recon.basic_fingerprint"]
        }
        res = self.app.post('/api/validate', headers=self.headers, data=json.dumps(fake_profile))
        self.assertEqual(res.status_code, 200)
        self.assertIn("valid", res.get_json())

    def test_missing_token_denied(self):
        res = self.app.get('/api/status')  # No token
        self.assertEqual(res.status_code, 401)

    def test_invalid_token_denied(self):
        res = self.app.get('/api/status', headers={"Authorization": "Bearer invalidtoken"})
        self.assertEqual(res.status_code, 403)

if __name__ == "__main__":
    unittest.main()

