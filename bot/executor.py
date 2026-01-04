
import subprocess
import os
from urllib.parse import quote
from bot.utils import git_commit
from bot.config import load_config


def clone_target_repo():
    config = load_config()
    token_name = config.get('github_token_secret', 'GITHUB_TOKEN')
    token = (os.environ.get(token_name) or "").strip()
    if not token:
        raise RuntimeError(f"Missing {token_name} in environment. Please add it as a repository secret and set github_token_secret in config.")
    # Safe debug (does not print the token)
    print(f"Auth env '{token_name}' detected (len={len(token)}).")

    gh_user = (config.get("github_username") or "").strip() or "x-access-token"
    gh_user_enc = quote(gh_user, safe="")
    token_enc = quote(token, safe="")
    # PATs are most reliable as https://<username>:<token>@github.com/<owner>/<repo>.git
    repo_url = f"https://{gh_user_enc}:{token_enc}@github.com/{config['target_repo']}.git"
    if not os.path.exists("target_repo"):
        subprocess.run(["git", "clone", repo_url, "target_repo"], check=True)
    # Ensure origin is correctly set for subsequent pushes (and not left blank)
    subprocess.run(["git", "remote", "set-url", "origin", repo_url], check=True, cwd="target_repo")
    # Ensure commits are attributed to a bot identity inside the target repo
    subprocess.run(["git", "config", "user.name", "Autonomous Bot"], check=True, cwd="target_repo")
    subprocess.run(["git", "config", "user.email", "autobot@users.noreply.github.com"], check=True, cwd="target_repo")


def execute_plan(plan, state):
    clone_target_repo()
    cwd = os.getcwd()
    os.chdir("target_repo")
    try:
        for step in plan:
            action = step['action']
            # Each action is mapped to a function
            if action == "add_html_structure":
                add_html_structure()
            elif action == "add_base_css":
                add_base_css()
            elif action == "add_favicon_robots":
                add_favicon_robots()
            elif action == "add_layout_system":
                add_layout_system()
            elif action == "add_typography":
                add_typography()
            elif action == "add_header":
                add_header()
            elif action == "refine_section":
                refine_section()
            elif action == "polish_micro":
                polish_micro()
            elif action == "accessibility":
                accessibility()
            else:
                raise Exception(f"Unknown action: {action}")
            git_commit(step['description'])
        subprocess.run(["git", "push", "origin", "HEAD:main"], check=True)
    finally:
        os.chdir(cwd)

def add_html_structure():
    # Write a minimal, semantic index.html
    os.makedirs("public", exist_ok=True)
    with open("public/index.html", "w") as f:
        f.write("""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
  <title>Professional Website</title>
  <link rel=\"icon\" href=\"/favicon.svg\" />
  <link rel=\"stylesheet\" href=\"/src/styles/base.css\" />
  <link rel=\"stylesheet\" href=\"/src/styles/theme.css\" />
</head>
<body>
  <div id=\"root\"></div>
  <script src=\"/src/main.tsx\" type=\"module\"></script>
</body>
</html>
""")

def add_base_css():
    os.makedirs("src/styles", exist_ok=True)
    with open("src/styles/base.css", "w") as f:
        f.write("""html {
  box-sizing: border-box;
  font-size: 16px;
}
*, *:before, *:after {
  box-sizing: inherit;
}
body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  transition: background 0.2s, color 0.2s;
}
""")

def add_favicon_robots():
    os.makedirs("public", exist_ok=True)
    with open("public/favicon.svg", "w") as f:
        f.write("""<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 64 64\"><rect width=\"64\" height=\"64\" rx=\"12\" fill=\"#222\"/><text x=\"50%\" y=\"54%\" text-anchor=\"middle\" font-size=\"32\" fill=\"#fff\" font-family=\"Inter,Segoe UI,Arial,sans-serif\" dy=\".3em\">W</text></svg>""")
    with open("public/robots.txt", "w") as f:
        f.write("User-agent: *\nDisallow:\n")

def add_layout_system():
    with open("src/styles/base.css", "a") as f:
        f.write("""
.container {
  max-width: 720px;
  margin: 0 auto;
  padding: 2rem 1rem;
}
""")

def add_typography():
    with open("src/styles/base.css", "a") as f:
        f.write("""
h1, h2, h3, h4, h5, h6 {
  font-weight: 600;
  margin: 0 0 0.5em 0;
}
p {
  margin: 0 0 1em 0;
  line-height: 1.6;
}
""")

def add_header():
    os.makedirs("src/components", exist_ok=True)
    with open("src/components/Header.tsx", "w") as f:
        f.write("""import React from 'react';
export default function Header() {
  return (
    <header className=\"container\" style={{paddingTop: '1.5rem', paddingBottom: '1.5rem'}}>
      <nav style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
        <span style={{fontWeight: 700, fontSize: '1.25rem'}}>Professional Website</span>
        <div>
          <a href=\"#about\" style={{marginRight: '1.5rem'}}>About</a>
          <a href=\"#contact\">Contact</a>
        </div>
      </nav>
    </header>
  );
}
""")

def refine_section():
    pass

def polish_micro():
    pass

def accessibility():
    pass
