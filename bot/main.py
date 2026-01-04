import sys
import subprocess

from bot.planner import plan_day
from bot.executor import execute_plan, clone_target_repo
from bot.config import load_config

def main():
    config = load_config()
    commits_per_day = int(config.get("min_commits_per_day", 3))
    total_days = int(config.get("project_duration", 60))

    # Ensure we have the target repo clone available for git-based state.
    clone_target_repo()

    # If we've already produced today's commits (rerun / retry), exit cleanly.
    today_count = subprocess.run(
        ["git", "-C", "target_repo", "log", "--since=midnight", "--oneline"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    commits_today = len([l for l in today_count.splitlines() if l.strip()])
    if commits_today >= commits_per_day:
        print(f"Already have {commits_today} commits today in target repo; nothing to do.")
        return

    # Derive day from total commit count in the target repo.
    total_commit_count = int(
        subprocess.run(
            ["git", "-C", "target_repo", "rev-list", "--count", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    current_day = max(1, (total_commit_count // commits_per_day) + 1)

    if current_day > total_days:
        print("Website build complete.")
        sys.exit(0)

    state = {"current_day": current_day, "total_days": total_days}
    plan = plan_day(state)
    execute_plan(plan)

if __name__ == "__main__":
    main()
