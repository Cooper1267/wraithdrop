import unittest
from flask import Flask
from api.controller import api_blueprint

class TestAPIAuth(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(api_blueprint, url_prefix="/api")
        self.client = self.app.test_client()

    def test_run_without_token(self):
        response = self.client.post("/api/run")
        self.assertEqual(response.status_code, 401)

    def test_run_with_invalid_token(self):
        response = self.client.post("/api/run", headers={"Authorization": "Bearer invalid-token"})
        self.assertEqual(response.status_code, 401)

    def test_run_with_valid_token(self):
        response = self.client.post("/api/run", headers={"Authorization": "Bearer secret-token-123"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("Authorized run initiated", response.get_json().get("message", ""))

if __name__ == "__main__":
    unittest.main()

