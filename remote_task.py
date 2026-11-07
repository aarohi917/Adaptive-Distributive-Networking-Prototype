
import subprocess
import sys

def run_remote_task(host, username, task_id):
    command = [
        "ssh",
        f"{username}@{host}",
        "python3",
        "compute_task.py",
        task_id,
    ]

    print(f"Sending task {task_id} to {host}...")

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("Remote task completed!")
            print("Raspberry Pi output:")
            print(result.stdout.strip())
        else:
            print("Remote task failed:")
            print(result.stderr.strip())

    except subprocess.TimeoutExpired:
        print("The remote task timed out.")
    except OSError as error:
        print(f"Could not start SSH: {error}")

if __name__ == "__main__":
    host = input("Raspberry Pi hostname or IP: ").strip()
    username = input("Raspberry Pi username: ").strip()
    task_id = input("Task ID (e.g. test-2): ").strip()

    if host and username and task_id:
        run_remote_task(host, username, task_id)
    else:
        print("Please enter all three values.")
