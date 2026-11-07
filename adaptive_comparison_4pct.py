
import csv
import json
import subprocess
import time
import psutil
from datetime import datetime
from pathlib import Path
from statistics import mean

USERNAME = "aarohikotkar"
HOST = "tks-pi.local"
OUTPUT_FILE = Path("adaptive_comparison_4pct_results.csv")
TRIALS = 5
CPU_THRESHOLD = 4

def run_laptop(task_id):
    from compute_task import run_task

    start = time.perf_counter()
    result = run_task(task_id)
    elapsed = time.perf_counter() - start

    return {
        "task_id": result["task_id"],
        "result_hash": result["result_hash"],
        "compute_seconds": result["duration_seconds"],
        "call_seconds": round(elapsed, 6),
    }


def run_pi(task_id):
    command = [
        "ssh", "-4",
        f"{USERNAME}@{HOST}",
        "python3", "~/compute_task.py", task_id
    ]

    start = time.perf_counter()
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=30
    )
    elapsed = time.perf_counter() - start

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    output = json.loads(result.stdout.strip())

    return {
        "task_id": output["task_id"],
        "result_hash": output["result_hash"],
        "compute_seconds": output["duration_seconds"],
        "call_seconds": round(elapsed, 6),
    }


def main():
    if OUTPUT_FILE.exists():
        print(f"STOP: {OUTPUT_FILE} already exists.")
        print("Rename or move it before running this experiment.")
        return

    rows = []

    # Measure baseline laptop CPU before each scheduling decision.
    for policy in ["fixed_laptop", "fixed_pi", "adaptive"]:
        print(f"\nTesting policy: {policy}")

        for trial in range(1, TRIALS + 1):
            task_id = f"trial-{trial}"
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent

            if policy == "fixed_laptop":
                node = "laptop"
            elif policy == "fixed_pi":
                node = "raspberry_pi"
            else:
                node = (
                    "raspberry_pi"
                    if cpu >= CPU_THRESHOLD
                    else "laptop"
                )

            try:
                if node == "laptop":
                    result = run_laptop(task_id)
                else:
                    result = run_pi(task_id)

                success = True
                error = ""

                print(
                    f"Trial {trial}: {node} | "
                    f"compute={result['compute_seconds']:.4f}s | "
                    f"call={result['call_seconds']:.4f}s"
                )

            except Exception as exc:
                result = {
                    "task_id": task_id,
                    "result_hash": "",
                    "compute_seconds": "",
                    "call_seconds": "",
                }
                success = False
                error = str(exc)
                print(f"Trial {trial} failed: {error}")

            rows.append({
                "timestamp": datetime.now().isoformat(),
                "policy": policy,
                "trial": trial,
                "task_id": task_id,
                "execution_node": node,
                "success": success,
                "compute_seconds": result["compute_seconds"],
                "call_seconds": result["call_seconds"],
                "laptop_cpu_percent": cpu,
                "laptop_memory_percent": memory,
                "result_hash": result["result_hash"],
                "error": error,
            })

    columns = list(rows[0].keys())

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nResults saved to {OUTPUT_FILE}")

    print("\nSUMMARY")
    for policy in ["fixed_laptop", "fixed_pi", "adaptive"]:
        successful = [
            row for row in rows
            if row["policy"] == policy and row["success"]
        ]
        if successful:
            avg_compute = mean(
                float(row["compute_seconds"]) for row in successful
            )
            avg_call = mean(
                float(row["call_seconds"]) for row in successful
            )
            print(
                f"{policy}: {len(successful)}/{TRIALS} successful; "
                f"mean compute={avg_compute:.4f}s; "
                f"mean elapsed={avg_call:.4f}s"
            )


if __name__ == "__main__":
    main()
