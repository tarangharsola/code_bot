from __future__ import annotations

from pathlib import Path

import yaml


def _repo_root() -> Path:
    # bot/config.py -> bot/ -> repo root
    return Path(__file__).resolve().parents[1]


def _parse_project_duration(raw_value):
    """Return an int day count or None for unlimited runtime."""
    if raw_value is None:
        return None
    if isinstance(raw_value, int):
        return None if raw_value <= 0 else raw_value
    if isinstance(raw_value, str):
        normalized = raw_value.strip().lower()
        if normalized in {"lifetime", "infinite", "forever", "unlimited", "none"}:
            return None
        try:
            parsed = int(normalized)
        except ValueError as exc:
            raise ValueError(
                "project_duration must be an integer day count or one of "
                "'lifetime', 'infinite', 'forever', 'unlimited', 'none'."
            ) from exc
        return None if parsed <= 0 else parsed
    raise ValueError("project_duration must be an integer or a string value.")


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

    config["project_duration_days"] = _parse_project_duration(config.get("project_duration"))
    return config
