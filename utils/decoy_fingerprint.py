import os
import platform
import socket
import uuid
import subprocess

def is_vm():
    vm_indicators = [
        'VBOX', 'VMware', 'QEMU', 'Hyper-V', 'KVM', 'Xen', 
        'VirtualBox', 'Parallels'
    ]
    try:
        system_product = subprocess.check_output(
            "wmic computersystem get model", shell=True
        ).decode().lower()
        for keyword in vm_indicators:
            if keyword.lower() in system_product:
                return True
    except Exception:
        pass
    return False

def suspicious_processes():
    suspicious = ['vmsrvc.exe', 'vmusrvc.exe', 'wireshark.exe', 'processhacker.exe']
    try:
        tasklist = subprocess.check_output("tasklist", shell=True).decode().lower()
        return any(proc.lower() in tasklist for proc in suspicious)
    except Exception:
        return False

def sandbox_fingerprint():
    flags = {
        "is_vm": is_vm(),
        "has_suspicious_processes": suspicious_processes(),
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "mac": uuid.getnode()
    }
    flags["is_sandbox"] = flags["is_vm"] or flags["has_suspicious_processes"]
    return flags

try:
    import psutil
except ImportError:
    psutil = None

class DecoyFingerprint:
    def __init__(self):
        self.hostname = socket.gethostname()
        self.username = os.getenv("USERNAME") or os.getenv("USER")
        self.os = platform.system().lower()

    def is_decoy(self):
        return (
            self._detect_vm_name() or
            self._detect_low_ram() or
            self._detect_user_pattern()
        )

    def _detect_vm_name(self):
        suspicious_names = ["sandbox", "maltest", "win7test", "malwarelab", "analysis", "vm"]
        for suspect in suspicious_names:
            if suspect in self.hostname.lower():
                return True
        return False

    def _detect_low_ram(self):
        if psutil:
            try:
                total_gb = psutil.virtual_memory().total / (1024**3)
                return total_gb < 2
            except Exception:
                return False
        return False

    def _detect_user_pattern(self):
        if not self.username:
            return False
        keywords = ["test", "analyst", "sandbox", "user", "vm"]
        return any(k in self.username.lower() for k in keywords)

# Expose is_decoy function for easy import
decoy = DecoyFingerprint()

def is_decoy():
    return decoy.is_decoy()

