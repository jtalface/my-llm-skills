"""
Fixed benchmark harness — DO NOT MODIFY.
Times process.py against sales.csv, median of 5 runs.
"""
import subprocess
import sys
import time
import statistics
import os

TARGET = [sys.executable, os.path.join(os.path.dirname(__file__), '..', 'target', 'process.py')]
RUNS = 5

# Sanity check: script must exit 0 and produce output.json
result = subprocess.run(TARGET, capture_output=True)
if result.returncode != 0:
    print(f"Sanity check failed:\n{result.stderr.decode()}", file=sys.stderr)
    sys.exit(1)

output_path = os.path.join(os.path.dirname(__file__), '..', 'target', 'output.json')
if not os.path.exists(output_path):
    print("Sanity check failed: output.json not produced", file=sys.stderr)
    sys.exit(1)

times = []
for _ in range(RUNS):
    t0 = time.perf_counter()
    subprocess.run(TARGET, capture_output=True)
    times.append((time.perf_counter() - t0) * 1000)

times.sort()
median = times[len(times) // 2]
print(f"runtime_ms: {median:.1f}")
print(f"all_runs: [{', '.join(f'{t:.1f}' for t in times)}]")
