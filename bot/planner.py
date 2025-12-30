from datetime import datetime

def plan_day(state):
    day = state['current_day']
    # Each day, plan 3 meaningful, incremental improvements
    # The plan is a list of 3 dicts: { "description": ..., "action": ... }
    # The planner is deterministic and idempotent per day
    plan = []
    # Example: day 1 = HTML skeleton, day 2 = layout, etc.
    if day == 1:
        plan = [
            {"description": "Add semantic HTML structure", "action": "add_html_structure"},
            {"description": "Add base CSS reset", "action": "add_base_css"},
            {"description": "Add favicon and robots.txt", "action": "add_favicon_robots"},
        ]
    elif day == 2:
        plan = [
            {"description": "Implement layout and spacing system", "action": "add_layout_system"},
            {"description": "Add modern, readable typography", "action": "add_typography"},
            {"description": "Add navigation header", "action": "add_header"},
        ]
    # ...continue for all 60 days...
    else:
        plan = [
            {"description": f"Refine section {day%5+1}", "action": "refine_section"},
            {"description": f"Polish micro-interactions {day%3+1}", "action": "polish_micro"},
            {"description": f"Accessibility improvement {day%4+1}", "action": "accessibility"},
        ]
    return plan
