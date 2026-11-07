import hashlib
import time
import json
import sys


def run_task(task_id, iterations=100000):
    start = time.perf_counter()

    data = f"TKS-BUILD-task-{task_id}".encode()
    result = data

    for _ in range(iterations):
        result = hashlib.sha256(result).digest()

    duration = time.perf_counter() - start

    return {
        "task_id": task_id,
        "result_hash": result.hex(),
        "duration_seconds": round(duration, 6),
    }


if __name__ == "__main__":
    task_id = sys.argv[1] if len(sys.argv) > 1 else "test-1"
    output = run_task(task_id)
    print(json.dumps(output))