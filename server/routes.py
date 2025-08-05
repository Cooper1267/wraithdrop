from flask import Flask, request, jsonify
from server.telemetry import log_telemetry
from utils.aes_encrypt import decrypt

app = Flask(__name__)

@app.route("/telemetry", methods=["POST"])
def receive_telemetry():
    try:
        encrypted = request.json.get("data")
        if not encrypted:
            return jsonify({"error": "Missing 'data' field"}), 400

        # Decrypt AES-wrapped payload
        event = decrypt(encrypted)

        # Log it using existing local logger
        log_telemetry(event)

        return jsonify({"status": "received"}), 200
    except Exception as e:
        return jsonify({"error": f"Decryption or logging failed: {str(e)}"}), 500

