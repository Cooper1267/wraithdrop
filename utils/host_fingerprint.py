# utils/host_fingerprint.py

import platform
import socket
import getpass
import uuid
import os

def get_mac_address():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                    for ele in range(0, 8 * 6, 8)][::-1])
    return mac

def get_hostname():
    return socket.gethostname()

def get_os_info():
    return f"{platform.system()} {platform.release()} ({platform.version()})"

def get_user():
    return getpass.getuser()

def get_cpu_info():
    return platform.processor()

def get_env_vars():
    return dict(os.environ)

def fingerprint():
    return {
        "hostname": get_hostname(),
        "user": get_user(),
        "os": get_os_info(),
        "mac": get_mac_address(),
        "cpu": get_cpu_info(),
        "env": {k: v for k, v in get_env_vars().items() if k.startswith('USER') or k.startswith('COMPUTER')}
    }

