import os
import platform
import socket
import uuid
import subprocess
import sys
import getpass

try:
    import psutil
except ImportError:
    psutil = None
    print("[WARN] psutil not installed: RAM detection disabled.", file=sys.stderr)

class DecoyFingerprint:
    def __init__(
        self,
        vm_name_keywords=None,
        suspicious_usernames=None,
        suspicious_processes=None,
        suspicious_env_vars=None,
        suspicious_files=None,
        min_ram_gb=2,
        debug=False
    ):
        self.hostname = socket.gethostname()
        self.username = os.getenv("USERNAME") or os.getenv("USER") or getpass.getuser()
        self.os = platform.system().lower()
        self.vm_name_keywords = vm_name_keywords or [
            "sandbox", "maltest", "win7test", "malwarelab", "analysis", "vm"
        ]
        self.suspicious_usernames = suspicious_usernames or [
            "test", "analyst", "sandbox", "user", "vm"
        ]
        self.suspicious_processes = suspicious_processes or [
            'vmsrvc.exe', 'vmusrvc.exe', 'wireshark.exe', 'processhacker.exe',
            'fiddler.exe', 'tcpview.exe', 'procmon.exe', 'procexp.exe',
            'ida.exe', 'ollydbg.exe', 'x64dbg.exe', 'x32dbg.exe', 
            'sandboxiedcomlaunch.exe', 'vmtoolsd.exe', 'vboxservice.exe'
        ]
        self.suspicious_env_vars = suspicious_env_vars or [
            'VBOX_', 'VMWARE_', 'SANDBOX_'
        ]
        self.suspicious_files = suspicious_files or [
            'C:\\windows\\system32\\drivers\\vmmouse.sys',
            'C:\\windows\\system32\\drivers\\vmhgfs.sys',
            '/etc/vbox_version',
            '/usr/bin/qemu-ga'
        ]
        self.min_ram_gb = min_ram_gb
        self.debug = debug

    def is_decoy(self):
        results = self.detect_all()
        score = sum(results.values())
        if self.debug:
            print(f"[DEBUG] Decoy score: {score} (details: {results})", file=sys.stderr)
        # Customize threshold as needed
        return score > 0

    def detect_all(self):
        results = {
            "vm_name": self._detect_vm_name(),
            "low_ram": self._detect_low_ram(),
            "user_pattern": self._detect_user_pattern(),
            "suspicious_process": self._detect_suspicious_process(),
            "suspicious_env": self._detect_suspicious_env(),
            "suspicious_file": self._detect_suspicious_file(),
            "virtual_mac": self._detect_virtual_mac(),
            "vm_manufacturer": self._detect_vm_manufacturer(),
        }
        return results

    def _detect_vm_name(self):
        for suspect in self.vm_name_keywords:
            if suspect in self.hostname.lower():
                return 1
        return 0

    def _detect_low_ram(self):
        if psutil:
            try:
                total_gb = psutil.virtual_memory().total / (1024**3)
                return 1 if total_gb < self.min_ram_gb else 0
            except Exception as e:
                if self.debug:
                    print(f"[DEBUG] _detect_low_ram() failed: {e}", file=sys.stderr)
        else:
            if self.debug:
                print("[WARN] psutil not available: skipping RAM check.", file=sys.stderr)
        return 0

    def _detect_user_pattern(self):
        if not self.username:
            return 0
        return 1 if any(k in self.username.lower() for k in self.suspicious_usernames) else 0

    def _detect_suspicious_process(self):
        try:
            if self.os == "windows":
                tasklist = subprocess.check_output("tasklist", shell=True).decode(errors='ignore').lower()
            else:
                tasklist = subprocess.check_output("ps aux", shell=True).decode(errors='ignore').lower()
            for proc in self.suspicious_processes:
                if proc.lower() in tasklist:
                    return 1
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] _detect_suspicious_process() failed: {e}", file=sys.stderr)
        return 0

    def _detect_suspicious_env(self):
        for env_var in self.suspicious_env_vars:
            for k, v in os.environ.items():
                if env_var in k or env_var in str(v):
                    return 1
        return 0

    def _detect_suspicious_file(self):
        for path in self.suspicious_files:
            if os.path.exists(path):
                return 1
        return 0

    def _detect_virtual_mac(self):
        try:
            mac = uuid.getnode()
            vm_mac_prefixes = [
                0x080027,  # VirtualBox
                0x000569,  # VMware
                0x000C29,  # VMware
                0x001C14,  # VMware
                0x005056,  # VMware
                0x00163E,  # Xen
            ]
            prefix = (mac >> 24) & 0xFFFFFF
            if prefix in vm_mac_prefixes:
                return 1
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] _detect_virtual_mac() failed: {e}", file=sys.stderr)
        return 0

    def _detect_vm_manufacturer(self):
        vm_indicators = [
            'VBOX', 'VMware', 'QEMU', 'Hyper-V', 'KVM', 'Xen', 
            'VirtualBox', 'Parallels'
        ]
        try:
            if self.os == "windows":
                system_product = subprocess.check_output(
                    "wmic computersystem get model", shell=True
                ).decode(errors='ignore').lower()
                for keyword in vm_indicators:
                    if keyword.lower() in system_product:
                        return 1
            else:
                if os.path.exists("/sys/class/dmi/id/product_name"):
                    with open("/sys/class/dmi/id/product_name") as f:
                        product_name = f.read().lower()
                    for keyword in vm_indicators:
                        if keyword.lower() in product_name:
                            return 1
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] _detect_vm_manufacturer() failed: {e}", file=sys.stderr)
        return 0

# Expose decoy instance and is_decoy function for easy import
decoy = DecoyFingerprint(debug=True)

def is_decoy():
    return decoy.is_decoy()

def decoy_details():
    return decoy.detect_all()
