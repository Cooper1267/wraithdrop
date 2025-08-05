def run(args):
    import subprocess
    result = subprocess.run(["whoami"], capture_output=True, text=True)
    return {
        "output": result.stdout.strip(),
        "error": result.stderr.strip(),
        "returncode": result.returncode,
        "success": result.returncode == 0
    }

