from __future__ import annotations

from pathlib import Path

import yaml


def _repo_root() -> Path:
    # bot/config.py -> bot/ -> repo root
    return Path(__file__).resolve().parents[1]


def load_config() -> dict:
    config_path = _repo_root() / "bot" / "user_config.yaml"
    if not config_path.exists():
        raise RuntimeError(
            f"User config not found. Please create {config_path.as_posix()} with required fields."
        )
    with config_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    required = [
        "user_name", "github_username", "target_repo", "github_token_secret",
        "project_prompt", "project_duration", "min_commits_per_day"
    ]
    for key in required:
        if key not in config:
            raise ValueError(f"Missing required config: {key}")
    return config
