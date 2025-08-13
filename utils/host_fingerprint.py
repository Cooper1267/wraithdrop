# utils/host_fingerprint.py

import platform
import socket
import getpass
import uuid
import os
import sys

def get_mac_address():
    try:
        mac = uuid.getnode()
        # Check if it's a real MAC (8th bit is not set)
        if (mac >> 40) % 2:
            return "unknown"
        mac_addr = ':'.join(['{:02x}'.format((mac >> ele) & 0xff)
                             for ele in range(0, 8 * 6, 8)][::-1])
        return mac_addr
    except Exception:
        return "unknown"

def get_hostname():
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"

def get_os_info():
    try:
        return f"{platform.system()} {platform.release()} ({platform.version()})"
    except Exception:
        return "unknown"

def get_user():
    try:
        return getpass.getuser()
    except Exception:
        return "unknown"

def get_cpu_info():
    try:
        cpu = platform.processor()
        if not cpu:
            # Fallback for Linux
            if sys.platform == "linux":
                try:
                    with open("/proc/cpuinfo") as f:
                        for line in f:
                            if "model name" in line:
                                return line.strip().split(":")[1].strip()
                except Exception:
                    pass
            # Fallback for macOS
            elif sys.platform == "darwin":
                try:
                    import subprocess
                    out = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"])
                    return out.decode().strip()
                except Exception:
                    pass
            # Fallback for Windows
            elif sys.platform == "win32":
                return os.environ.get("PROCESSOR_IDENTIFIER", "unknown")
            return "unknown"
        return cpu
    except Exception:
        return "unknown"

def get_env_vars():
    # Only include non-sensitive environment variables commonly used for user/host identification.
    safe_keys = {"USER", "USERNAME", "COMPUTERNAME", "HOSTNAME", "LOGNAME"}
    env = {}
    for k in safe_keys:
        val = os.environ.get(k)
        if val is not None:
            env[k] = val
    return env

def fingerprint():
    return {
        "hostname": get_hostname(),
        "user": get_user(),
        "os": get_os_info(),
        "mac": get_mac_address(),
        "cpu": get_cpu_info(),
        "env": get_env_vars(),
    }
