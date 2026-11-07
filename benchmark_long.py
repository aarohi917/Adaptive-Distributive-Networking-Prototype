
import base64
import csv
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from statistics import mean

import psutil
from compute_task import run_task


# ---------------- CONFIGURATION ----------------

USERNAME = "aarohikotkar"
HOST = "192.168.0.8"

ITERATIONS = 5_000_000
TRIALS = 3
CPU_THRESHOLD = 4.0

OUTPUT_FILE = Path("benchmark_long_results_v5.csv")

# ------------------------------------------------


def run_laptop(task_id):
    """Run a task locally on the Windows laptop."""
    start = time.perf_counter()
    result = run_task(task_id, ITERATIONS)
    elapsed = time.perf_counter() - start

    return {
        "node": "laptop",
        "compute_seconds": result["duration_seconds"],
        "elapsed_seconds": elapsed,
        "result_hash": result["result_hash"],
    }


def run_pi(task_id):
    """Run a task remotely on the Raspberry Pi."""
    remote_python = (
        "import json; "
        "from compute_task import run_task; "
        f"print(json.dumps(run_task({json.dumps(task_id)}, {ITERATIONS})))"
    )

    encoded_command = base64.b64encode(
        remote_python.encode("utf-8")
    ).decode("ascii")

    remote_command = (
        "cd ~/Solar_AI_Satellite 2>/dev/null || cd ~; "
        f"echo {encoded_command} | base64 -d | python3"
    )

    command = [
        "ssh",
        "-4",
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=5",
        "-o", "ServerAliveInterval=10",
        f"{USERNAME}@{HOST}",
        remote_command,
    ]

    start = time.perf_counter()

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=180,
    )

    elapsed = time.perf_counter() - start

    if completed.returncode != 0:
        raise RuntimeError(
            f"SSH/remote task failed: {completed.stderr.strip()}"
        )

    output_lines = [
        line.strip()
        for line in completed.stdout.splitlines()
        if line.strip()
    ]

    if not output_lines:
        raise RuntimeError("The Raspberry Pi returned no task result.")

    result = json.loads(output_lines[-1])

    return {
        "node": "raspberry_pi",
        "compute_seconds": result["duration_seconds"],
        "elapsed_seconds": elapsed,
        "result_hash": result["result_hash"],
    }


def get_system_stats():
    """Capture laptop CPU and memory usage at the decision point."""
    cpu = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    return cpu, memory


def run_policy(policy, trial_number):
    """Run one trial using the selected placement policy."""
    task_id = f"{policy}-trial-{trial_number}"

    cpu, memory = get_system_stats()

    if policy == "fixed_laptop":
        selected_node = "laptop"
        result = run_laptop(task_id)

    elif policy == "fixed_pi":
        selected_node = "raspberry_pi"
        result = run_pi(task_id)

    elif policy == "adaptive":
        if cpu >= CPU_THRESHOLD:
            selected_node = "raspberry_pi"
        else:
            selected_node = "laptop"

        if selected_node == "raspberry_pi":
            result = run_pi(task_id)
        else:
            result = run_laptop(task_id)

    else:
        raise ValueError(f"Unknown policy: {policy}")

    # Verify the task output against a local reference calculation.
    reference = run_task(task_id, ITERATIONS)
    hash_match = result["result_hash"] == reference["result_hash"]

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "policy": policy,
        "trial": trial_number,
        "iterations": ITERATIONS,
        "cpu_percent_at_decision": round(cpu, 2),
        "memory_percent_at_decision": round(memory, 2),
        "cpu_threshold_percent": CPU_THRESHOLD,
        "selected_node": selected_node,
        "reported_node": result["node"],
        "compute_seconds": round(result["compute_seconds"], 4),
        "elapsed_seconds": round(result["elapsed_seconds"], 4),
        "hash_match": hash_match,
        "success": hash_match,
        "error": "",
    }


def main():
    policies = ["fixed_laptop", "fixed_pi", "adaptive"]

    columns = [
        "timestamp",
        "policy",
        "trial",
        "iterations",
        "cpu_percent_at_decision",
        "memory_percent_at_decision",
        "cpu_threshold_percent",
        "selected_node",
        "reported_node",
        "compute_seconds",
        "elapsed_seconds",
        "hash_match",
        "success",
        "error",
    ]

    all_results = []

    print("=" * 65)
    print("LONG BENCHMARK: LAPTOP vs RASPBERRY PI vs ADAPTIVE")
    print(f"Iterations per task: {ITERATIONS:,}")
    print(f"Trials per policy: {TRIALS}")
    print(f"Adaptive CPU threshold: {CPU_THRESHOLD}%")
    print(f"Results file: {OUTPUT_FILE}")
    print("=" * 65)

    # Check SSH before running the benchmark.
    print("\nChecking Raspberry Pi SSH connection...")

    try:
        check = subprocess.run(
            [
                "ssh",
                "-4",
                "-o", "BatchMode=yes",
                "-o", "ConnectTimeout=5",
                f"{USERNAME}@{HOST}",
                "hostname",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if check.returncode != 0:
            print("SSH CHECK FAILED:")
            print(check.stderr.strip())
            print("No benchmark was started.")
            return

        print("Connected to:", check.stdout.strip())

    except Exception as exc:
        print("SSH CHECK FAILED:", exc)
        print("No benchmark was started.")
        return

    start_time = time.perf_counter()

    for policy in policies:
        print(f"\nTesting {policy} — {ITERATIONS:,} iterations per task")

        for trial in range(1, TRIALS + 1):
            try:
                row = run_policy(policy, trial)
                all_results.append(row)

                print(
                    f"Trial {trial}: {row['reported_node']}; "
                    f"compute={row['compute_seconds']:.3f}s; "
                    f"elapsed={row['elapsed_seconds']:.3f}s; "
                    f"hash_match={row['hash_match']}"
                )

            except Exception as exc:
                print(f"Trial {trial} FAILED: {exc}")

                all_results.append({
                    "timestamp": datetime.now().isoformat(
                        timespec="seconds"
                    ),
                    "policy": policy,
                    "trial": trial,
                    "iterations": ITERATIONS,
                    "cpu_percent_at_decision": "",
                    "memory_percent_at_decision": "",
                    "cpu_threshold_percent": CPU_THRESHOLD,
                    "selected_node": "",
                    "reported_node": "",
                    "compute_seconds": "",
                    "elapsed_seconds": "",
                    "hash_match": False,
                    "success": False,
                    "error": str(exc),
                })

    total_elapsed = time.perf_counter() - start_time

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(all_results)

    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)

    for policy in policies:
        rows = [r for r in all_results if r["policy"] == policy]
        successful = [
            r for r in rows
            if r["success"] and r["elapsed_seconds"] != ""
        ]

        if not successful:
            print(f"{policy}: no successful trials")
            continue

        compute_times = [r["compute_seconds"] for r in successful]
        elapsed_times = [r["elapsed_seconds"] for r in successful]

        print(
            f"{policy}: {len(successful)}/{TRIALS} successful; "
            f"mean compute={mean(compute_times):.3f}s; "
            f"mean elapsed={mean(elapsed_times):.3f}s"
        )

        print(
            "  Nodes selected:",
            ", ".join(r["reported_node"] for r in successful),
        )

    print(f"\nTotal benchmark time: {total_elapsed:.1f}s")
    print(f"Saved results to: {OUTPUT_FILE.resolve()}")
    print("Benchmark finished.")


if __name__ == "__main__":
    main()
