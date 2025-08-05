# utils/sandbox_detect.py

import os
import platform
import time
import getpass
import uuid
import subprocess

def check_cpu_count():
    count = os.cpu_count()
    return count is not None and count <= 2

def check_username():
    suspicious_users = ['sandbox', 'user', 'admin', 'test']
    current = getpass.getuser().lower()
    return current in suspicious_users

def check_uptime():
    # Simulated timing trick (clock skew detection)
    start = time.time()
    time.sleep(0.01)
    end = time.time()
    return (end - start) < 0.005  # too fast = possible virtualization time warp

def check_mac_address():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                    for ele in range(0, 8*6, 8)][::-1])
    return mac.startswith("00:05:69") or mac.startswith("00:0C:29")  # VMware/VirtualBox prefixes

def check_known_sandbox_processes():
    try:
        output = subprocess.check_output("tasklist", shell=True).decode().lower()
        sandboxes = ['vboxservice', 'vboxtray', 'vmtoolsd', 'wireshark']
        return any(proc in output for proc in sandboxes)
    except:
        return False  # safe default

def run_all_checks():
    results = {
        "low_cpu": check_cpu_count(),
        "suspicious_user": check_username(),
        "fast_sleep": check_uptime(),
        "sandbox_mac": check_mac_address(),
        "suspicious_process": check_known_sandbox_processes()
    }

    suspicious = [k for k, v in results.items() if v]
    verdict = len(suspicious) >= 2

    return verdict, results

