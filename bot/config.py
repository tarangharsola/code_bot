import os
import yaml

CONFIG_PATH = "bot/user_config.yaml"

def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise RuntimeError(
            f"User config not found. Please create {CONFIG_PATH} with required fields."
        )
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
    required = [
        "user_name", "github_username", "target_repo", "github_token_secret",
        "project_prompt", "project_duration", "min_commits_per_day"
    ]
    for key in required:
        if key not in config:
            raise ValueError(f"Missing required config: {key}")
    return config
