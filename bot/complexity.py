import sys
import time
import tracemalloc

def check_complexity():
    # Example: check that planner and executor are O(1) per day
    # (In real system, would analyze call counts, file accesses, etc.)
    # Here, we simulate by timing and memory snapshot
    start = time.time()
    tracemalloc.start()
    from bot.planner import plan_day
    from bot.state import get_state
    plan_day(get_state())
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed = time.time() - start
    if elapsed > 2.0:
        print("Complexity check failed: execution time too high")
        sys.exit(1)
    if peak > 10_000_000:
        print("Complexity check failed: memory usage too high")
        sys.exit(1)
    print("Complexity check passed.")

if __name__ == "__main__":
    check_complexity()
