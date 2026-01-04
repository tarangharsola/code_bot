import os
import subprocess
import sys
from bot.config import load_config

def check_commits():
    config = load_config()
    # Count today's commits in the target repository clone
    target_dir = "target_repo"
    if not os.path.exists(target_dir) or not os.path.exists(os.path.join(target_dir, '.git')):
        print("ERROR: target_repo is not present. Ensure the executor successfully cloned the target repository.")
        sys.exit(1)
    result = subprocess.run(
        ["git", "-C", target_dir, "log", "--since=midnight", "--oneline"],
        capture_output=True, text=True
    )
    count = len([line for line in result.stdout.strip().splitlines() if line.strip()])
    min_commits = config["min_commits_per_day"]
    if count < min_commits:
        print(f"ERROR: Only {count} commits today in target repo, required minimum is {min_commits}")
        sys.exit(1)
    print(f"Commit check passed: {count} commits today in target repo.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "check_commits":
        check_commits()
