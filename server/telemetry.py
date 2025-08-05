import json
import os
import requests
from datetime import datetime
from flask import Blueprint, request, jsonify
from utils.aes_encrypt import encrypt, decrypt  # You need both encrypt and decrypt

LOG_DIR = "logs"
REMOTE_SERVER = "http://localhost:7000"  # or external URL

telemetry_bp = Blueprint('telemetry', __name__)  # Create blueprint

def get_fingerprint():
    # Placeholder: implement your host fingerprint logic or import it
    return "host-fingerprint-placeholder"

def log_telemetry(event: dict):
    print(f"[DEBUG] Logging event: {event.get('event', 'unknown')}")
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"{date_str}.log")

    event["timestamp"] = now.strftime("%Y-%m-%d %H:%M:%S")
    event["host"] = get_fingerprint()

    # Write locally
    with open(log_file, "a") as f:
        f.write(json.dumps(event) + "\n")

    print(f"[📡 Logged] {event.get('profile')} | {event.get('action')} → {event.get('details')}")

    # Send encrypted to remote
    try:
        payload = {"data": encrypt(event)}
        requests.post(f"{REMOTE_SERVER}/telemetry", json=payload, timeout=2)
    except Exception as e:
        print(f"[⚠️] Failed to POST telemetry: {e}")

@telemetry_bp.route("/telemetry", methods=["POST"])
def receive_telemetry():
    try:
        encrypted = request.json.get("data")
        if not encrypted:
            return jsonify({"error": "Missing 'data' field"}), 400

        event = decrypt(encrypted)
        log_telemetry(event)
        return jsonify({"status": "received"}), 200

    except Exception as e:
        return jsonify({"error": f"Decryption or logging failed: {str(e)}"}), 500

