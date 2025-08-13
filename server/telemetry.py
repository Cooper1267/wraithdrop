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
    # Ensure event is serializable before processing
    try:
        json.dumps(event)
    except Exception as e:
        print(f"[⚠️] Event not serializable: {e}")
        return

    if not os.path.exists(LOG_DIR):
        try:
            os.makedirs(LOG_DIR)
            print(f"[DEBUG] Created log directory: {LOG_DIR}")
        except Exception as e:
            print(f"[⚠️] Failed to create log directory: {e}")
            return

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"{date_str}.log")

    event["timestamp"] = now.strftime("%Y-%m-%d %H:%M:%S")
    event["host"] = get_fingerprint()

    # Write locally
    try:
        with open(log_file, "a") as f:
            f.write(json.dumps(event) + "\n")
        print(f"[📡 Logged] {event.get('profile')} | {event.get('action')} → {event.get('details')}")
    except Exception as e:
        print(f"[⚠️] Failed to write log: {e}")

    # Send encrypted to remote
    try:
        print(f"[DEBUG] Event before encryption: {event}")
        payload = {"data": encrypt(event)}
        print(f"[DEBUG] Encrypted payload: {payload}")
        response = requests.post(f"{REMOTE_SERVER}/telemetry", json=payload, timeout=2)
        print(f"[DEBUG] Remote POST status: {response.status_code}")
    except Exception as e:
        print(f"[⚠️] Failed to POST telemetry: {e}")

@telemetry_bp.route("/telemetry", methods=["POST"])
def receive_telemetry():
    try:
        print(f"[DEBUG] Incoming request: {request.json}")
        encrypted = request.json.get("data")
        if not encrypted:
            print(f"[⚠️] Missing 'data' field in incoming request.")
            return jsonify({"error": "Missing 'data' field"}), 400

        event = decrypt(encrypted)
        print(f"[DEBUG] Decrypted event: {event}")
        log_telemetry(event)
        return jsonify({"status": "received"}), 200

    except Exception as e:
        print(f"[⚠️] Decryption or logging failed: {e}")
        return jsonify({"error": f"Decryption or logging failed: {str(e)}"}), 500

# For direct testing (optional)
if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(telemetry_bp)
    app.run(debug=True, port=5000)
