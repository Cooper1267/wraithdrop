from flask import Flask, request, jsonify
from server.telemetry import log_telemetry
from utils.aes_encrypt import decrypt
import traceback

app = Flask(__name__)

@app.route("/telemetry", methods=["POST"])
def receive_telemetry():
    try:
        print("Incoming request JSON:", request.json)
        encrypted = request.json.get("data")
        if not encrypted:
            print("Error: 'data' field missing in request")
            return jsonify({"error": "Missing 'data' field"}), 400

        # Decrypt AES-wrapped payload
        try:
            event = decrypt(encrypted)
            print("Decrypted event:", event)
        except Exception as dec_err:
            print("Decryption failed:", dec_err)
            traceback.print_exc()
            return jsonify({"error": f"Decryption failed: {str(dec_err)}"}), 400

        # Log it using existing local logger
        try:
            log_telemetry(event)
            print("Telemetry logged successfully")
        except Exception as log_err:
            print("Logging failed:", log_err)
            traceback.print_exc()
            return jsonify({"error": f"Logging failed: {str(log_err)}"}), 500

        return jsonify({"status": "received"}), 200
    except Exception as e:
        print("General Exception:", e)
        traceback.print_exc()
        return jsonify({"error": f"Decryption or logging failed: {str(e)}"}), 500
