import hashlib
import time
import csv
from datetime import datetime


def run_task(task_number, iterations=100000):
    """Run a repeatable computing task and return its result."""
    data = f"TKS-BUILD-task-{task_number}".encode()
    result = data

    for _ in range(iterations):
        result = hashlib.sha256(result).digest()

    return result.hex()


def main():
    filename = "experiment_results.csv"

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "timestamp",
            "policy",
            "task_number",
            "execution_node",
            "success",
            "duration_seconds",
        ])

        for policy in ["fixed", "adaptive"]:
            print(f"\nRunning {policy} policy...")

            for task_number in range(1, 4):
                start = time.perf_counter()

                try:
                    run_task(task_number)
                    success = True
                except Exception as error:
                    print(f"Task failed: {error}")
                    success = False

                duration = time.perf_counter() - start

                writer.writerow([
                    datetime.now().isoformat(),
                    policy,
                    task_number,
                    "laptop",
                    success,
                    round(duration, 4),
                ])

                print(
                    f"Task {task_number}: "
                    f"{duration:.4f} seconds | "
                    f"Success: {success}"
                )

    print(f"\nResults saved to {filename}")
    print("Note: both policies currently run on the laptop.")


if __name__ == "__main__":
    main()