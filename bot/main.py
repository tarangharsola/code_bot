import sys
from bot.planner import plan_day
from bot.executor import execute_plan
from bot.state import get_state, save_state

def main():
    state = get_state()
    today = state['current_day']
    if today > state['total_days']:
        print("Website build complete.")
        sys.exit(0)
    plan = plan_day(state)
    execute_plan(plan, state)
    state['current_day'] += 1
    save_state(state)

if __name__ == "__main__":
    main()
