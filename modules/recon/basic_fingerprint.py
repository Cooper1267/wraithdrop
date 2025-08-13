from utils.payload_runner import PayloadRunner

def run(dry_run=False):
    runner = PayloadRunner(dry_run=dry_run)
    results = {}
    payloads = [
        ("whoami", runner.simulate_whoami),
        ("netstat", runner.simulate_netstat),
        ("reg_query", runner.simulate_reg_query)
    ]

    for name, method in payloads:
        try:
            print(f"[DEBUG] Running payload: {name}")
            result = method()
            print(f"[DEBUG] Payload {name} result: {result}")
            results[name] = result
        except Exception as e:
            print(f"[ERROR] Exception while executing payload '{name}': {e}")
            results[name] = f"Error: {e}"

    return {
        "module": "basic_fingerprint",
        "payloads_executed": [name for name, _ in payloads],
        "results": results
    }
