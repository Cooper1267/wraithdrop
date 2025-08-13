from flask import Blueprint, request, jsonify
from api.auth import require_token  # your token decorator; consistent naming!
from utils.payload_runner import PayloadRunner
from utils.cli_profile_builder import load_profile
from utils.decoy_fingerprint import is_decoy
from modules.recon import basic_fingerprint
import logging
import threading
import os

api_blueprint = Blueprint('api', __name__)

# Thread-safe command queue
COMMAND_QUEUE = {}
COMMAND_QUEUE_LOCK = threading.Lock()

# Configurable log file path
LOG_PATH = os.environ.get("WRAITHDROP_LOG_PATH", "telemetry/logs.jsonl")

# Setup logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wraithdrop.api")

@api_blueprint.route('/run', methods=['POST'])
@require_token
def run_profile(current_user):
    data = request.get_json()
    if not data or "ttp" not in data:
        logger.warning("Missing 'ttp' field in request")
        return jsonify({"error": "Missing 'ttp' field in request"}), 400

    ttp_path = data["ttp"]

    try:
        profile = load_profile(ttp_path)
    except Exception as e:
        logger.exception("Failed to load TTP profile")
        return jsonify({"error": f"Failed to load TTP profile: {str(e)}"}), 500

    results = []
    for step in profile.get("steps", []):
        if step == "recon.basic_fingerprint":
            if is_decoy():
                results.append({"step": step, "skipped": True})
                continue
            result = basic_fingerprint.run()
            results.append({"step": step, "result": result})
        else:
            results.append({"step": step, "error": "Unknown step"})

    return jsonify({"results": results})

@api_blueprint.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "WraithDrop API is running"})

@api_blueprint.route('/logs', methods=['GET'])
@require_token
def logs(current_user):
    # Restrict access to logs for only admins or privileged users if possible
    # For now, just log access
    logger.info("User %s accessed logs", getattr(current_user, "username", None))
    try:
        if not os.path.exists(LOG_PATH):
            return jsonify({"logs": []})
        with open(LOG_PATH, "r") as f:
            lines = f.readlines()[-50:]
            return jsonify({"logs": lines})
    except Exception as e:
        logger.exception("Failed to read logs")
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/validate', methods=['POST'])
@require_token
def validate_profile(current_user):
    data = request.get_json()
    if not data or "ttp" not in data:
        logger.warning("Missing 'ttp' field in validate request")
        return jsonify({"error": "Missing 'ttp' field in request"}), 400

    try:
        profile = load_profile(data["ttp"])
        return jsonify({"valid": True, "steps": profile.get("steps", [])})
    except Exception as e:
        logger.exception("Failed to validate profile")
        return jsonify({"valid": False, "error": str(e)}), 400

@api_blueprint.app_errorhandler(404)
def not_found(error):
    logger.warning("404 Not Found: %s", request.path)
    return jsonify({"error": "Route not found"}), 404

@api_blueprint.app_errorhandler(500)
def server_error(error):
    logger.error("500 Internal Server Error: %s", str(error))
    return jsonify({"error": "Internal server error"}), 500

@api_blueprint.route("/poll", methods=["GET"])
@require_token
def poll_command(current_user):
    client_id = request.args.get("client_id", "default")
    with COMMAND_QUEUE_LOCK:
        queue = COMMAND_QUEUE.get(client_id, [])
        if queue:
            task = queue.pop(0)
            # Clean up empty lists
            if not queue:
                del COMMAND_QUEUE[client_id]
            logger.info("Polled task for client_id=%s: %s", client_id, task)
            return jsonify({"task": task})
    return jsonify({"task": None})

@api_blueprint.route("/enqueue", methods=["POST"])
@require_token
def enqueue_command(current_user):
    data = request.get_json()
    client_id = data.get("client_id", "default")
    task = data.get("task")
    if not task:
        logger.warning("No task provided to enqueue")
        return jsonify({"error": "No task provided"}), 400
    with COMMAND_QUEUE_LOCK:
        COMMAND_QUEUE.setdefault(client_id, []).append(task)
    logger.info("Enqueued task for client_id=%s: %s", client_id, task)
    return jsonify({"status": "Task queued"})
