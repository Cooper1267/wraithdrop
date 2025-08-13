def run(args):
    import subprocess

    try:
        # Attempt to run the "whoami" command
        result = subprocess.run(
            ["whoami"],
            capture_output=True,
            text=True,
            check=True  # Raises CalledProcessError if returncode != 0
        )
        output = result.stdout.strip()
        error = result.stderr.strip()
        returncode = result.returncode
        success = True
    except subprocess.CalledProcessError as e:
        # Command failed: capture output and error
        output = e.stdout.strip() if e.stdout else ""
        error = e.stderr.strip() if e.stderr else str(e)
        returncode = e.returncode if hasattr(e, "returncode") else -1
        success = False
    except Exception as ex:
        # Unexpected error: return as error string
        output = ""
        error = str(ex)
        returncode = -1
        success = False

    # Use print statements for output (for debugging)
    print(f"output: {output}")
    print(f"error: {error}")
    print(f"returncode: {returncode}")
    print(f"success: {success}")

    return {
        "output": output,
        "error": error,
        "returncode": returncode,
        "success": success
    }
