
import subprocess
import json
import time
import psutil
import csv
from datetime import datetime

HOST = "tks-pi.local"
USERNAME = "aarohikotkar"
RESULTS_FILE = "distributed_test_results.csv"


def run_pi_task(task_id):
    """Send a computing task to the Raspberry Pi over SSH."""
    command = [
        "ssh",
        "-4",
        f"{USERNAME}@{HOST}",
        "python3",
        "~/compute_task.py",
        task_id,
    ]

    start = time.perf_counter()

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=30,
    )

    elapsed = time.perf_counter() - start

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    output = json.loads(result.stdout.strip())

    return output, elapsed


def main():
    print("TKS BUILD: Laptop-to-Pi distributed test")
    print("Checking laptop resources...")

    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent

    print(f"Laptop CPU usage: {cpu:.1f}%")
    print(f"Laptop memory usage: {memory:.1f}%")
    print("\nSending a task to the Raspberry Pi...")

    try:
        output, elapsed = run_pi_task("distributed-test-1")

        print("\nSUCCESS: Raspberry Pi completed the task!")
        print(f"Task ID: {output['task_id']}")
        print(f"Pi computation time: {output['duration_seconds']} seconds")
        print(f"Total remote-call time: {elapsed:.4f} seconds")
        print(f"Result hash: {output['result_hash']}")

        with open(RESULTS_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "timestamp",
                "task_id",
                "execution_node",
                "success",
                "pi_compute_seconds",
                "remote_call_seconds",
                "laptop_cpu_percent",
                "laptop_memory_percent",
                "result_hash",
            ])
            writer.writerow([
                datetime.now().isoformat(),
                output["task_id"],
                "raspberry_pi",
                True,
                output["duration_seconds"],
                round(elapsed, 6),
                cpu,
                memory,
                output["result_hash"],
            ])

        print(f"\nResults saved to {RESULTS_FILE}")

    except Exception as error:
        print("\nTASK FAILED")
        print(f"Error: {error}")
        print("No successful result was recorded.")


if __name__ == "__main__":
    main()
