import subprocess

def git_commit(message):
    subprocess.run(["git", "add", "."], check=True)
    # Only commit if there are staged changes
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode == 1:
        subprocess.run(["git", "commit", "-m", message], check=True)
