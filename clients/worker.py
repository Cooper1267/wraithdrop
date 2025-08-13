# client/worker.py
import requests
import time
import os
from datetime import datetime
from server.emulator import Emulator
from utils.host_fingerprint import fingerprint

SERVER_URL = "http://localhost:7000"  # Change if deployed
PROFILE_DIR = "ttp_profiles"

host_fp = fingerprint()

def log_telemetry(data):
    # Placeholder for telemetry logging, could be sending to server, logging, etc.
    print(f"[TELEMETRY] {data}")

log_telemetry({
    "event": "host_fingerprint",
    "profiles": "system_boot",
    "details": host_fp,
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
})

def get_task():
    try:
        res = requests.get(f"{SERVER_URL}/task")
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print(f"Failed to fetch task: {e}")
    return None

def main():
    while True:
        task = get_task()
        if task and 'profile' in task:
            profile_name = task['profile']
            profile_path = os.path.join(PROFILE_DIR, profile_name)
            if os.path.exists(profile_path):
                print(f"🧠 Running profile: {profile_name}")
                emulator = Emulator(profile_path)
                emulator.run()
            else:
                print(f"❌ Profile not found: {profile_name}")
        else:
            print("🕸️ No task received. Sleeping...")
        time.sleep(10)  # Polling interval

if __name__ == "__main__":
    main()
