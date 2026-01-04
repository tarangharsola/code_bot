def plan_day(state):
    day = state['current_day']
    # Always generate 6 meaningful, incremental improvements per day
    plan = []
    if day == 1:
        plan = [
            {"description": "Scaffold Vite + React + TS", "action": "scaffold_frontend"},
            {"description": "Add base styling + layout", "action": "add_base_styles"},
            {"description": "Add Monaco editor", "action": "add_monaco_editor"},
            {"description": "Add Yjs realtime collaboration", "action": "add_yjs_collab"},
            {"description": "Add collaborative room routing", "action": "add_room_routing"},
            {"description": "Add collaboration server + docs", "action": "add_server_and_docs"},
        ]
    else:
        # For subsequent days, rotate through refinement, polish, accessibility, and other improvements
        for i in range(6):
            if i % 3 == 0:
                plan.append({"description": f"Improve connection UX {i+1}", "action": "improve_connection_ux"})
            elif i % 3 == 1:
                plan.append({"description": f"Improve presence panel {i+1}", "action": "improve_presence_panel"})
            else:
                plan.append({"description": f"Improve editor ergonomics {i+1}", "action": "improve_editor_ergonomics"})
    return plan
