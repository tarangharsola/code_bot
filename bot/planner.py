def plan_day(state):
    day = state['current_day']
    # Always generate 6 meaningful, incremental improvements per day
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
        plan = [
            {"description": f"AI: {t}", "action": "ai_step", "task": t}
            for t in tasks
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
        plan = [
            {"description": f"AI: {t}", "action": "ai_step", "task": t}
            for t in rotated[:6]
        ]
    return plan
