# Adaptive-Distributive-Networking-Prototype
Project Overview

This project investigates how adaptive task scheduling across multiple computing nodes can improve computational performance and energy efficiency.

Hardware

Lenovo Windows 11 laptop (8 GB RAM)

Raspberry Pi 4 (4 GB RAM)

How It Works

The prototype uses an adaptive scheduler to monitor laptop CPU utilization and distribute computational tasks between two computing nodes.

The scheduler uses a 4% CPU utilization threshold to determine when tasks should be offloaded to the Raspberry Pi.

Technology

Python

SHA-256 hashing

SSH communication

CPU utilization monitoring

Repository Contents

compute_task.py: Computational workload

adaptive_comparison_4pct.py: Adaptive scheduling comparison

energy_comparison.py: Energy benchmarking

benchmark_long.py: Long-duration performance testing

CSV files: Experimental results

Results

In a 300-task benchmark, distributed execution reduced total completion time from 1,203 seconds to 724 seconds, approximately a 39.8% reduction.

Limitations

This prototype uses two computing nodes connected over a local Wi-Fi network. Energy measurements are preliminary and communication overhead remains an area for improvement.
