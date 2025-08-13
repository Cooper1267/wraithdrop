import requests
import json
import time
import sys
import os
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from utils.aes_encrypt import encrypt  # your encryption function
except Exception as import_error:
    print(f"[ERROR] Failed to import encrypt: {import_error}")
    traceback.print_exc()
    sys.exit(1)

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
    print("[DEBUG] Generated event:", json.dumps(event, indent=2))
    return event

def send_telemetry(event):
    try:
        encrypted_data = encrypt(event)
        print("[DEBUG] Encrypted data:", encrypted_data)
        payload = {"data": encrypted_data}
        print("[DEBUG] Payload to send:", payload)
        resp = requests.post(TELEMETRY_URL, json=payload, timeout=10)
        print(f"[INFO] Sent event: {event['event']} | Status: {resp.status_code}")
        print(f"[DEBUG] Response content: {resp.content.decode(errors='replace')}")
    except Exception as e:
        print(f"[ERROR] Failed to send telemetry: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    while True:
        evt = generate_event()
        send_telemetry(evt)
        time.sleep(5)  # send every 5 seconds
