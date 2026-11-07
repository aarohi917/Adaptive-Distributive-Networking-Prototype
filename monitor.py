
import time
import psutil

print("Laptop system monitor")
print("Press Ctrl+C to stop.\n")

try:
    while True:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent

        print(
            f"CPU usage: {cpu_usage:5.1f}% | "
            f"Memory usage: {memory_usage:5.1f}%"
        )

        time.sleep(1)

except KeyboardInterrupt:
    print("\nMonitoring stopped.")
