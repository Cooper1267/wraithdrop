import os
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
        results[name] = method()

    return {
        "module": "basic_fingerprint",
        "payloads_executed": [name for name, _ in payloads],
        "results": results
    }

