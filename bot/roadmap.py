from bot.config import load_config

def generate_roadmap():
    config = load_config()
    days = config["project_duration"]
    prompt = config["project_prompt"]
    constraints = config.get("constraints", [])
    # Deterministic, idempotent roadmap generation
    roadmap = []
    for day in range(1, days + 1):
        roadmap.append({
            "day": day,
            "tasks": [
                f"Task {i+1} for day {day} based on prompt: {prompt} and constraints: {constraints}"
                for i in range(config["min_commits_per_day"])
            ]
        })
    return roadmap
