import time
import random
import yaml
import os
from datetime import datetime
from server.telemetry import log_telemetry
from utils.sandbox_detect import run_all_checks
from utils.aes_encrypt import encrypt, decrypt  # NEW: AES import

def safe_filename(filename):
    """Sanitize filename to avoid directory traversal."""
    return os.path.basename(filename)

class Emulator:
    def __init__(self, profile_path: str):
        print(f"[DEBUG] Loading profile from: {profile_path}")
        try:
            with open(profile_path, 'r') as file:
                self.profile = yaml.safe_load(file)
        except Exception as e:
            print(f"[ERROR] Failed to load profile: {e}")
            raise

        # Defensive: Check profile is dict
        if not isinstance(self.profile, dict):
            raise ValueError("Profile YAML is not a dictionary.")

        self.name = self.profile.get("name", "Unnamed Profile")
        self.actions = self.profile.get("actions", [])
        if not isinstance(self.actions, list):
            raise ValueError("Profile 'actions' must be a list.")
        print(f"[DEBUG] Profile loaded: {self.profile}")
        print(f"[DEBUG] Emulator name set to: {self.name}")
        print(f"[DEBUG] Total actions loaded: {len(self.actions)}")
        self.results = []

    def run(self):
        try:
            start_time = self.now()
            print(f"[{start_time}] ⚙️  Starting emulator: {self.name}")

            log_telemetry({
                "event": "emulator_start",
                "profile": self.name,
                "timestamp": start_time
            })
            print("[DEBUG] Logged emulator_start")

            for i, action in enumerate(self.actions):
                step_time = self.now()
                action_type = action.get('type', 'unknown')
                print(f"[{step_time}] → Step {i+1}: {action_type}")

                result = self.simulate_action(action)
                print(f"[DEBUG] simulate_action result: {result}")

                if result == "ABORT":
                    print(f"[{self.now()}] ⚠️ Emulator aborted due to sandbox detection.")
                    log_telemetry({
                        "event": "emulator_aborted",
                        "profile": self.name,
                        "step": i + 1,
                        "reason": "sandbox_detected",
                        "timestamp": self.now()
                    })
                    print("[DEBUG] Logged emulator_aborted")
                    return

                self.results.append(result)

                log_telemetry({
                    "event": "emulator_step",
                    "profile": self.name,
                    "step": i + 1,
                    "action": action_type,
                    "details": result,
                    "timestamp": step_time
                })
                print("[DEBUG] Logged emulator_step")

                time.sleep(random.uniform(0.3, 1.2))  # Simulated delay

            end_time = self.now()
            print(f"[{end_time}] ✅ Emulator complete.")
            log_telemetry({
                "event": "emulator_end",
                "profile": self.name,
                "steps": len(self.actions),
                "timestamp": end_time
            })
            print("[DEBUG] Logged emulator_end")
        except Exception as e:
            print(f"[ERROR] Emulator crashed: {e}")
            log_telemetry({
                "event": "emulator_crash",
                "profile": getattr(self, 'name', 'unknown'),
                "error": str(e),
                "timestamp": self.now()
            })

    def simulate_action(self, action: dict):
        t = action.get('type')

        if t == "scan":
            ports = action.get("ports", [])
            targets = action.get("targets", ["127.0.0.1"])
            return f"Scanned ports {ports} on {len(targets)} targets"

        elif t == "brute_force":
            proto = action.get("protocol", "unknown")
            creds = action.get("creds", [])
            return f"Tried {len(creds)} fake {proto} logins"

        elif t == "drop":
            filename = safe_filename(action.get("filename", "payload.bin"))
            return f"Fake dropped file: {filename}"

        elif t == "report":
            return f"Reported: {action.get('format', 'generic')}"

        elif t == "drop_enc":
            filename = safe_filename(action.get("filename", "stage2_payload.enc"))
            payload = action.get("payload", "simulated_payload")
            encrypted = encrypt({"payload": payload})

            os.makedirs("dropped", exist_ok=True)
            # Write as text, ensure str
            mode = "w"
            data = encrypted if isinstance(encrypted, str) else encrypted.decode('utf-8', errors='replace')
            try:
                with open(os.path.join("dropped", filename), mode) as f:
                    f.write(data)
            except Exception as e:
                return f"Failed to write encrypted payload: {str(e)}"
            return f"Encrypted payload dropped as {filename}"

        elif t == "decrypt_payload":
            filename = safe_filename(action.get("filename", "stage2_payload.enc"))
            try:
                with open(os.path.join("dropped", filename), "r") as f:
                    data = f.read()
                decrypted = decrypt(data)
                if not isinstance(decrypted, dict):
                    return f"Decryption output not dict: {decrypted}"
                return f"Decrypted payload: {decrypted.get('payload', '[no payload]')}"
            except Exception as e:
                return f"Decryption failed: {str(e)}"

        elif t == "detect_env":
            try:
                detected, details = run_all_checks()
            except Exception as e:
                log_telemetry({
                    "event": "sandbox_check",
                    "profile": self.name,
                    "result": "error",
                    "details": str(e),
                    "timestamp": self.now()
                })
                return f"Sandbox check failed: {str(e)}"

            log_telemetry({
                "event": "sandbox_check",
                "profile": self.name,
                "result": "detected" if detected else "clean",
                "details": details,
                "timestamp": self.now()
            })

            if action.get("exit_on_detection", False) and detected:
                return "ABORT"
            return f"Sandbox check complete. Verdict: {'DETECTED' if detected else 'CLEAN'}"

        else:
            return f"Unknown action type: {t}"

    def now(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
