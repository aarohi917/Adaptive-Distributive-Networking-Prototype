
import csv
import time
import threading
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from compute_task import run_task

TASK_COUNT = 6
LAPTOP_SLOTS = 4
ITERATIONS = 5_000_000

OUTPUT = Path("task_A_repeat3_results.csv")


def execute_task(task_number, submitted_at, semaphore):
    task_id = f"task_A_{task_number}"

    # Only four tasks can hold a laptop execution slot at once.
    with semaphore:
        started_at = time.perf_counter()
        queue_wait = started_at - submitted_at

        try:
            result = run_task(task_id, iterations=ITERATIONS)
            success = True
            result_hash = result.get("result_hash", "")
            error = ""
        except Exception as exc:
            success = False
            result_hash = ""
            error = str(exc)

        finished_at = time.perf_counter()

    return {
        "task_id": task_id,
        "node": "laptop",
        "queue_wait_seconds": queue_wait,
        "execution_seconds": finished_at - started_at,
        "completion_seconds": finished_at - submitted_at,
        "success": success,
        "result_hash": result_hash,
        "error": error,
    }


def main():
    if OUTPUT.exists():
        print("STOP: results file already exists:", OUTPUT)
        print("Existing results have not been changed.")
        return

    print("TASK A: FIXED LAPTOP SCHEDULING")
    print("Tasks submitted:", TASK_COUNT)
    print("Maximum concurrent laptop tasks:", LAPTOP_SLOTS)
    print("Iterations per task:", ITERATIONS)
    print("Raspberry Pi: NOT USED")
    print()

    semaphore = threading.Semaphore(LAPTOP_SLOTS)
    rows = []

    # All six jobs are submitted to the executor together.
    submitted_at = time.perf_counter()

    with ThreadPoolExecutor(max_workers=TASK_COUNT) as pool:
        futures = [
            pool.submit(execute_task, number, submitted_at, semaphore)
            for number in range(1, TASK_COUNT + 1)
        ]

        for future in as_completed(futures):
            row = future.result()
            rows.append(row)

            print(
                f"{row['task_id']}: "
                f"queue wait={row['queue_wait_seconds']:.3f}s, "
                f"execution={row['execution_seconds']:.3f}s, "
                f"completion={row['completion_seconds']:.3f}s, "
                f"success={row['success']}"
            )

    fields = [
        "task_id",
        "node",
        "queue_wait_seconds",
        "execution_seconds",
        "completion_seconds",
        "success",
        "result_hash",
        "error",
    ]

    # Write rows in task-number order for easier analysis.
    rows.sort(key=lambda row: row["task_id"])

    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    successful = sum(row["success"] for row in rows)
    makespan = max(
        (float(row["completion_seconds"]) for row in rows),
        default=0
    )

    print("\nTASK A COMPLETE")
    print(f"Successful tasks: {successful}/{TASK_COUNT}")
    print(f"Overall makespan: {makespan:.3f} seconds")
    print("Results saved to:", OUTPUT)
    print("Timestamp:", datetime.now().isoformat())


if __name__ == "__main__":
    main()
