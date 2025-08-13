import eventlet
eventlet.monkey_patch()

import sys
import os
import json
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

LOG_DIR = "../logs"

def load_logs():
    logs = []
    abs_log_dir = os.path.abspath(LOG_DIR)
    print(f"[DEBUG] Log directory: {abs_log_dir}")
    if not os.path.exists(LOG_DIR):
        print(f"[WARNING] Log directory does not exist: {abs_log_dir}")
        return logs

    for fname in sorted(os.listdir(LOG_DIR)):
        if fname.endswith(".log"):
            with open(os.path.join(LOG_DIR, fname), 'r') as file:
                for line in file:
                    try:
                        parsed = json.loads(line.strip())
                        if isinstance(parsed, dict):
                            logs.append(parsed)
                    except json.JSONDecodeError as e:
                        print(f"[ERROR] Could not parse line in {fname}: {e}")
                        continue
    logs.sort(key=lambda x: x.get("timestamp") if isinstance(x, dict) else "", reverse=True)
    print(f"[DEBUG] Loaded {len(logs)} log entries.")
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
            print(f"[DEBUG] Log entry missing host: {entry}")
        grouped[host].append(entry)
    for host, entries in grouped.items():
        print(f"[DEBUG] {host}: {len(entries)} logs")
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
    try:
        return jsonify(grouped)
    except TypeError as e:
        # JSON serialization error, log which host/log entry caused it
        print(f"[ERROR] Could not jsonify grouped logs: {e}")
        return jsonify({"error": "Could not serialize logs"}), 500

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
                print(f"[DEBUG] Emitting new log: {uid}")
                socketio.emit("new_log", log)
        eventlet.sleep(2)

@socketio.on('connect')
def handle_connect():
    print("[🔌] Client connected.")

if __name__ == "__main__":
    print("[INFO] Starting SocketIO background log watcher...")
    socketio.start_background_task(watch_logs)
    socketio.run(app, host="0.0.0.0", port=7000, debug=True)
