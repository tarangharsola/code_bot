import subprocess
import sys
from bot.config import load_config
from bot.state import get_state

def git_commit(message):
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)

def check_commits():
    state = get_state()
    config = load_config()
    today = state["current_day"]
    # Count today's commits
    result = subprocess.run(
        ["git", "log", "--since=midnight", "--oneline"],
        capture_output=True, text=True
    )
    count = len(result.stdout.strip().splitlines())
    min_commits = config["min_commits_per_day"]
    if count < min_commits:
        print(f"ERROR: Only {count} commits today, required minimum is {min_commits}")
        sys.exit(1)
    print(f"Commit check passed: {count} commits today.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "check_commits":
        check_commits()
