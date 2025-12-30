import json
import os

STATE_PATH = os.environ.get("BOT_STATE_PATH", "bot/state.json")

def get_state():
    if not os.path.exists(STATE_PATH):
        state = {
            "current_day": 1,
            "total_days": 60,
            "history": [],
        }
        save_state(state)
        return state
    with open(STATE_PATH, "r") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)
