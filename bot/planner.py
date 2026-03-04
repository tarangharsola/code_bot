import random
from bot.config import load_config

def plan_day(state):
    day = state['current_day']
    config = load_config()
    min_commits = int(config.get("min_commits_per_day", 6))
    # No upper limit: use all available tasks, repeat if needed, but always at least 6
    # If you want to allow more, expand the tasks list or logic
    plan = []
    if day == 1:
        tasks = [
            "Scaffold a production-ready web app project (frontend + backend if needed) with clear run instructions.",
            "Implement the core UI shell and routing for shareable collaborative rooms (unique URLs).",
            "Add a real code editor component with syntax highlighting for JavaScript, Python, and HTML.",
            "Add real-time sync using a CRDT/OT library and a WebSocket server (no placeholders).",
            "Add live cursor/presence indicators + active users panel with stable colors.",
            "Add robust connection/reconnection UX and update README with complete local run steps."
        ]
        num_commits = max(min_commits, len(tasks))
        full_tasks = (tasks * ((num_commits // len(tasks)) + 1))[:num_commits]
        plan = [
            {"description": f"AI: {t}", "action": "ai_step", "task": t}
            for t in full_tasks
        ]
    else:
        tasks = [
            "Harden realtime collaboration: conflict handling, reconnection, and awareness consistency.",
            "Improve editor UX: language switching, formatting defaults, and better keyboard shortcuts.",
            "Add connection status indicator and retry/backoff behavior.",
            "Improve active users panel and cursor labels (no neon/purple; readable on dark mode).",
            "Add basic tests or smoke checks and a build script so CI can validate the app.",
            "Refactor for maintainability: split modules, improve types, and reduce complexity hotspots."
        ]
        # Rotate tasks by day so work changes over time.
        rotated = tasks[day % len(tasks):] + tasks[: day % len(tasks)]
        num_commits = max(min_commits, len(rotated))
        full_tasks = (rotated * ((num_commits // len(rotated)) + 1))[:num_commits]
        plan = [
            {"description": f"AI: {t}", "action": "ai_step", "task": t}
            for t in full_tasks
        ]
    return plan
