import subprocess
import platform
import shlex

class PayloadRunner:
    def __init__(self, log_func=None, dry_run=False):
        self.log = log_func if log_func else self._default_logger
        self.dry_run = dry_run
        self.os = platform.system().lower()

    def _default_logger(self, msg):
        print(f"[PayloadRunner] {msg}")

    def run(self, command):
        self.log(f"Executing payload: {command}")
        if self.dry_run:
            self.log("Dry run enabled — skipping execution.")
            return {"output": f"simulated dry run for: {command}", "error": "", "returncode": 0, "success": True}

        try:
            if isinstance(command, str):
                command = shlex.split(command)
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            return {
                "output": result.stdout.strip(),
                "error": result.stderr.strip(),
                "returncode": result.returncode,
                "success": result.returncode == 0
            }
        except Exception as e:
            return {
                "output": "",
                "error": str(e),
                "returncode": -1,
                "success": False
            }

    def simulate_whoami(self):
        return self.run("whoami")

    def simulate_netstat(self):
        if self.os == "windows":
            return self.run("netstat -ano")
        else:
            return self.run("netstat -tunlp")

    def simulate_reg_query(self, path="HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"):
        if self.os != "windows":
            return {"output": "", "error": "reg query not supported on this OS", "returncode": 1, "success": False}
        return self.run(f'reg query "{path}"')

