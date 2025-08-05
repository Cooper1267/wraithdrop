import requests
import json
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.aes_encrypt import encrypt  # your encryption function

TELEMETRY_URL = "http://localhost:7000/api/telemetry"  # Adjust if needed

def generate_event():
    event = {
        "event": "test_event",
        "profile": "simulator",
        "action": "ping",
        "details": {
            "hostname": "simulated_host",
            "info": "Simulated telemetry event"
        }
    }
    return event

def send_telemetry(event):
    encrypted_data = encrypt(event)
    payload = {"data": encrypted_data}
    try:
        resp = requests.post(TELEMETRY_URL, json=payload, timeout=10)
        print(f"Sent event: {event['event']} | Status: {resp.status_code}")
    except Exception as e:
        print(f"Failed to send telemetry: {e}")

if __name__ == "__main__":
    while True:
        evt = generate_event()
        send_telemetry(evt)
        time.sleep(5)  # send every 5 seconds

