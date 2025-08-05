import unittest
from flask import json
from wraithdrop_main import create_app

VALID_TOKEN = "secret-token" # Match this with your api/auth.py

class TestAPIEndpoints(unittest.TestCase):
def setUp(self):
    self.app = create_app(testing=True)
    self.client = self.app.test_client()

def test_run_without_token_should_fail(self):
    response = self.client.post("/api/run")
    self.assertEqual(response.status_code, 401)
    self.assertIn("Unauthorized", response.get_data(as_text=True))

def test_run_with_invalid_token_should_fail(self):
    headers = {"Authorization": "Bearer wrong-token"}
    response = self.client.post("/api/run", headers=headers)
    self.assertEqual(response.status_code, 401)
    self.assertIn("Unauthorized", response.get_data(as_text=True))

def test_run_with_valid_token_should_pass(self):
    headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
    response = self.client.post("/api/run", headers=headers)
    self.assertEqual(response.status_code, 200)
    self.assertIn("Authorized run initiated", response.get_data(as_text=True))
if name == "main":
unittest.main()
