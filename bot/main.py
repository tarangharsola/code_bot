import sys
import subprocess
import time
from datetime import datetime, timedelta

from bot.planner import plan_day
from bot.executor import execute_plan, clone_target_repo
from bot.config import load_config

def main():
    config = load_config()
    commits_per_day = int(config.get("min_commits_per_day", 3))
    total_days = int(config.get("project_duration", 60))
    min_commit_interval_hours = int(config.get("min_commit_interval_hours", 3))

    # Ensure we have the target repo clone available for git-based state.
    clone_target_repo()

    # Get today's commits and their timestamps
    today_count = subprocess.run(
        ["git", "-C", "target_repo", "log", "--since=midnight", "--pretty=%ct"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    commit_times = [int(l.strip()) for l in today_count.splitlines() if l.strip()]
    commits_today = len(commit_times)
    now = int(time.time())

    # Enforce minimum interval only after daily minimum is reached.
    if commit_times and commits_today >= commits_per_day:
        last_commit_time = max(commit_times)
        next_allowed_time = last_commit_time + min_commit_interval_hours * 3600
        if now < next_allowed_time:
            wait_minutes = int((next_allowed_time - now) / 60)
            print(f"Last commit was too recent. Next commit allowed in {wait_minutes} minutes.")
            return

    # Derive day from bot-authored commits only, so existing repo history doesn't block progress.
    bot_log = subprocess.run(
        ["git", "-C", "target_repo", "log", "--grep=^BOT:", "--oneline"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    bot_commit_count = len([line for line in bot_log.splitlines() if line.strip()])
    if bot_commit_count == 0:
        current_day = 1
    else:
        current_day = (bot_commit_count // commits_per_day) + 1

    if current_day > total_days:
        print("Website build complete.")
        sys.exit(0)

    state = {"current_day": current_day, "total_days": total_days}
    plan = plan_day(state)
    # Only block if fewer than min_commits_per_day and interval not met; allow extra commits if planner generates more steps.
    if commits_today < commits_per_day:
        execute_plan(plan)
    else:
        print(f"Minimum {commits_per_day} commits reached; allowing extra commits if planner generates more steps.")
        execute_plan(plan)

if __name__ == "__main__":
    main()
