
# Solar-Powered AI Satellite Network
# Step 4: Power-aware AI task scheduling

satellites = {
    "Satellite A": {
        "power": 25,
        "available": True,
        "capacity": 1
    },
    "Satellite B": {
        "power": 85,
        "available": True,
        "capacity": 3
    },
}

tasks = {
    "Basic image analysis": 1,
    "Advanced AI image analysis": 3,
}

def choose_satellite(task_name):
    required_capacity = tasks[task_name]
    candidates = []

    for name, satellite in satellites.items():
        if not satellite["available"]:
            continue

        if satellite["capacity"] < required_capacity:
            continue

        if satellite["power"] < 15:
            continue

        candidates.append((name, satellite["power"]))

    if not candidates:
        return None

    return max(candidates, key=lambda item: item[1])[0]


print("=== POWER-AWARE AI TASK SCHEDULER ===")

for task_name in tasks:
    print(f"\nTask: {task_name}")
    print(f"Required capacity: {tasks[task_name]}")

    selected = choose_satellite(task_name)

    if selected:
        print(f"Assigned to: {selected}")
        print("Decision: TASK ACCEPTED")
    else:
        print("Assigned to: None")
        print("Decision: NO SUITABLE SATELLITE")

print("\nTask scheduling simulation complete!")
