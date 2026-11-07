
import csv
import subprocess
import sys
import time
from pathlib import Path

# Run from the Solar_AI_Satellite project folder.
BASE_DIR = Path(__file__).resolve().parent
SOURCE = BASE_DIR / "six_task_capacity_test.py"
SUMMARY = BASE_DIR / "energy_batch_A_50_results.csv"

BATCH_COUNT = 50
TIMEOUT_SECONDS = 180

def main():
    if not SOURCE.exists():
        print(f"STOP: Source script not found: {SOURCE}")
        return

    if SUMMARY.exists():
        print(f"STOP: {SUMMARY.name} already exists.")
        print("Rename it before running to preserve previous results.")
        return

    source_text = SOURCE.read_text(encoding="utf-8")

    original_output = 'task_A_fixed_scheduling_results.csv'
    if original_output not in source_text:
        print("STOP: Could not find the expected output filename")
        print("inside six_task_capacity_test.py.")
        print("No batches were run.")
        return

    summary_rows = []
    total_elapsed = 0.0

    for batch in range(1, BATCH_COUNT + 1):
        output_name = f"task_A_energy_batch50_{batch}.csv"
        batch_output = BASE_DIR / output_name
        temp_script = BASE_DIR / f"_task_A_energy_run_{batch}.py"

        if batch_output.exists():
            print(f"STOP: {output_name} already exists.")
            print("No file will be overwritten. Rename the existing")
            print("file or use a different batch filename before retrying.")
            break

        modified_source = source_text.replace(
            original_output, output_name
        )
        temp_script.write_text(modified_source, encoding="utf-8")

        print(f"\n{'=' * 55}")
        print(f"TASK A ENERGY BATCH {batch}/{BATCH_COUNT}")
        print("Six tasks on laptop; Raspberry Pi powered on and idle.")
        print(f"Output: {output_name}")
        print(f"{'=' * 55}", flush=True)

        start = time.perf_counter()
        success = False
        output_text = ""
        error_text = ""

        try:
            result = subprocess.run(
                [sys.executable, str(temp_script)],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                errors="replace",
            )
            output_text = result.stdout or ""
            error_text = result.stderr or ""

            print(output_text, end="")
            if error_text:
                print("\n--- STDERR ---")
                print(error_text)

            success = (
                result.returncode == 0
                and "TASK A COMPLETE" in output_text
                and "Successful tasks: 6/6" in output_text
                and "Overall makespan:" in output_text
                and batch_output.exists()
            )

            if result.returncode != 0:
                print(f"Script exit code: {result.returncode}")

        except subprocess.TimeoutExpired as exc:
            output_text = str(exc.stdout or "")
            error_text = str(exc.stderr or "")
            print(f"ERROR: Batch exceeded {TIMEOUT_SECONDS} seconds.")

        except Exception as exc:
            error_text = repr(exc)
            print(f"ERROR: {exc}")

        finally:
            elapsed = time.perf_counter() - start
            temp_script.unlink(missing_ok=True)

        total_elapsed += elapsed
        summary_rows.append({
            "batch": batch,
            "success": success,
            "elapsed_seconds": round(elapsed, 3),
            "output_file": output_name,
            "details": (
                "6/6 tasks succeeded"
                if success
                else (error_text.strip() or "Batch did not meet success checks")
            ),
        })

        print(f"\nBatch elapsed: {elapsed:.3f} seconds")
        print(f"Batch successful: {success}")

        # Save progress after every batch, including any failure.
        # This helps preserve results if the overall run is interrupted.
        with SUMMARY.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "batch",
                    "success",
                    "elapsed_seconds",
                    "output_file",
                    "details",
                ],
            )
            writer.writeheader()
            writer.writerows(summary_rows)

        if not success:
            print("\nSTOPPING: This batch did not pass all success checks.")
            print("Review its output before deciding whether to continue.")
            break

    successful = sum(row["success"] for row in summary_rows)

    print("\nTASK A ENERGY SUMMARY")
    print(f"Batches attempted: {len(summary_rows)}/{BATCH_COUNT}")
    print(f"Successful batches: {successful}/{len(summary_rows)}")
    print(f"Total elapsed: {total_elapsed:.3f} seconds")
    print(f"Summary saved to: {SUMMARY.name}")

    if len(summary_rows) == BATCH_COUNT and successful == BATCH_COUNT:
        print("ALL 50 BATCHES COMPLETED SUCCESSFULLY.")
    else:
        print("The 50-batch run is incomplete; inspect the summary before retrying.")

if __name__ == "__main__":
    main()
