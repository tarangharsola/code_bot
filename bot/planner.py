from datetime import datetime

def plan_day(state):
    day = state['current_day']
    # Always generate 6 meaningful, incremental improvements per day
    plan = []
    if day == 1:
        plan = [
            {"description": "Add semantic HTML structure", "action": "add_html_structure"},
            {"description": "Add base CSS reset", "action": "add_base_css"},
            {"description": "Add favicon and robots.txt", "action": "add_favicon_robots"},
            {"description": "Add layout system", "action": "add_layout_system"},
            {"description": "Add typography", "action": "add_typography"},
            {"description": "Add navigation header", "action": "add_header"},
        ]
    else:
        # For subsequent days, rotate through refinement, polish, accessibility, and other improvements
        for i in range(6):
            if i % 3 == 0:
                plan.append({"description": f"Refine section {(day+i)%5+1}", "action": "refine_section"})
            elif i % 3 == 1:
                plan.append({"description": f"Polish micro-interactions {(day+i)%3+1}", "action": "polish_micro"})
            else:
                plan.append({"description": f"Accessibility improvement {(day+i)%4+1}", "action": "accessibility"})
    return plan
