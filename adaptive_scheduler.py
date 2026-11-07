

import psutil
import time


def measure_laptop():
    """Measure actual laptop CPU and memory usage."""
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent

    return {
        "cpu_percent": cpu,
        "memory_percent": memory,
    }


def choose_node(laptop, pi_available=False):
    """Choose a node using measured laptop CPU usage."""
    if not pi_available:
        return "laptop", "Raspberry Pi not connected"

    if laptop["cpu_percent"] >= 70:
        return "raspberry_pi", "Laptop CPU usage is high"

    return "laptop", "Laptop CPU usage is below the threshold"


def main():
    print("Adaptive scheduler - monitoring test")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            laptop = measure_laptop()

            # TEST ONLY: simulate Pi availability.
            pi_available = True

            node, reason = choose_node(laptop, pi_available)

            print(f"Laptop CPU: {laptop['cpu_percent']:.1f}%")
            print(f"Laptop memory: {laptop['memory_percent']:.1f}%")
            print(f"Chosen node: {node}")
            print(f"Reason: {reason}")
            print("-" * 35)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")


if __name__ == "__main__":
    main()
