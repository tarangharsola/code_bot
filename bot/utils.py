import subprocess
from bot.config import load_config

def git_commit(message):
    config = load_config()
    github_username = (config.get("github_username") or "").strip()
    user_name = (config.get("user_name") or github_username or "Autonomous Bot").strip()
    user_email = (config.get("git_email") or f"{github_username}@users.noreply.github.com" or "autobot@users.noreply.github.com").strip()

    # Set user details for commit attribution
    subprocess.run(["git", "config", "user.name", user_name], check=True)
    subprocess.run(["git", "config", "user.email", user_email], check=True)
    subprocess.run(["git", "add", "."], check=True)
    # Only commit if there are staged changes
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode == 1:
        subprocess.run(["git", "commit", "-m", message], check=True)
