import os
import json
import time
import tracemalloc

PERF_FILE = "bot/perf_baseline.json"
TOLERANCE = 1.15  # 15% regression allowed

def main():
    start = time.time()
    tracemalloc.start()
    from bot.planner import plan_day
    from bot.state import get_state
    plan_day(get_state())
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed = time.time() - start

    if os.path.exists(PERF_FILE):
        with open(PERF_FILE, "r") as f:
            baseline = json.load(f)
        if elapsed > baseline["elapsed"] * TOLERANCE:
            print("Performance regression: time exceeded")
            exit(1)
        if peak > baseline["peak"] * TOLERANCE:
            print("Performance regression: memory exceeded")
            exit(1)
    # Update baseline
    with open(PERF_FILE, "w") as f:
        json.dump({"elapsed": elapsed, "peak": peak}, f)
    print("Performance check passed.")

if __name__ == "__main__":
    main()
