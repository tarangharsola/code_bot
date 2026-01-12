import subprocess

def git_commit(message):
    # Set user details for commit attribution
    subprocess.run(["git", "config", "user.name", "tarangharsola"], check=True)
    subprocess.run(["git", "config", "user.email", "tarang.harsola@gmail.com"], check=True)
    subprocess.run(["git", "add", "."], check=True)
    # Only commit if there are staged changes
    result = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if result.returncode == 1:
        subprocess.run(["git", "commit", "-m", message], check=True)
