import eventlet
eventlet.monkey_patch()

import sys
import os
import json
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from collections import defaultdict
from server.telemetry import telemetry_bp

# Add parent dir so 'api' and 'dashboard' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api.controller import api_blueprint  # your API routes

app = Flask(__name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../dashboard/templates')))
app.register_blueprint(telemetry_bp, url_prefix="/api")
app.register_blueprint(api_blueprint, url_prefix="/api")


socketio = SocketIO(app, async_mode='eventlet')

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")

def load_logs():
    logs = []
    if not os.path.exists(LOG_DIR):
        return logs

    for fname in sorted(os.listdir(LOG_DIR)):
        if fname.endswith(".log"):
            with open(os.path.join(LOG_DIR, fname), 'r') as file:
                for line in file:
                    try:
                        parsed = json.loads(line.strip())
                        if isinstance(parsed, dict):
                            logs.append(parsed)
                    except json.JSONDecodeError:
                        continue
    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return logs

def group_by_host(logs):
    grouped = defaultdict(list)
    for entry in logs:
        if not isinstance(entry, dict):
            continue
        details = entry.get("details")
        host = None
        if isinstance(details, dict):
            host = details.get("hostname")
        if not host:
            host = entry.get("host")
        if not host:
            host = "unknown"
        grouped[host].append(entry)
    return grouped

@app.route("/")
def index():
    logs = load_logs()
    grouped = group_by_host(logs)
    return render_template("index.html", grouped_logs=grouped)

@app.route("/api/grouped-logs")
def api_grouped_logs():
    logs = load_logs()
    grouped = group_by_host(logs)
    return jsonify(grouped)

def watch_logs():
    seen = set()
    while True:
        logs = load_logs()
        for log in logs:
            if not isinstance(log, dict):
                continue
            timestamp = log.get('timestamp')
            event = log.get('event')
            profile = log.get('profile')
            if not (timestamp and event and profile):
                continue
            uid = f"{timestamp}_{event}_{profile}"
            if uid not in seen:
                seen.add(uid)
                socketio.emit("new_log", log)
        eventlet.sleep(2)

@socketio.on('connect')
def handle_connect():
    print("[🔌] Client connected.")

if __name__ == "__main__":
    socketio.start_background_task(watch_logs)
    socketio.run(app, host="0.0.0.0", port=7000, debug=True)

