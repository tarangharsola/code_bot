# Autonomous Collaborative Code Editor Bot

This project is a fully autonomous system that incrementally builds a collaborative code editor web application over 60 days, making exactly 6 real Git commits every day. The bot runs in the cloud via GitHub Actions and enforces complexity and performance checks on every run.

## Features
- **Collaborative Code Editor:** Real-time multi-user editing with syntax highlighting for JavaScript, Python, and HTML.
- **Live Cursors & User Presence:** See each user's cursor, name, and color. Active users panel displays all connected participants.
- **Document Sharing:** Unique shareable URLs for each coding session.
- **Responsive UI:** Clean, professional interface with dark mode and mobile/desktop support.
- **Robust Backend:** Uses WebSocket for real-time sync, CRDT/OT for conflict resolution, and production-grade error handling.
- **Autonomous Development:** Bot plans, implements, and commits 6 incremental improvements every day for 60 days.
- **Cloud Execution:** Runs daily in GitHub Actions at 12:00 PM IST (06:30 UTC) and can be manually triggered.
- **Complexity & Performance Checks:** Ensures efficient, scalable code with every commit.

## How It Works
- The bot lives in the `code_bot` repository and writes code into the target repo (`awesome-project`).
- Every day, the bot:
  1. Clones the target repo
  2. Plans 6 incremental improvements
  3. Applies changes, commits, and pushes
  4. Enforces commit policy and performance checks
- All configuration is managed via `bot/user_config.yaml`.

## Setup
1. **Create a Personal Access Token (PAT):**
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate a token with `public_repo` (for public repos) or `repo` (for private repos)
2. **Add the PAT to Secrets:**
   - In the `code_bot` repo, go to Settings → Secrets and variables → Actions
   - Add a new secret named `TARGET_REPO_PAT` with your token value
3. **Configure the Bot:**
   - Edit `bot/user_config.yaml` to set your GitHub username, target repo, and project prompt

## Running Locally
```sh
# Set your PAT in the environment
$env:TARGET_REPO_PAT = "<your_token>"
python -m bot.main
```

## Cloud Execution
- The bot runs automatically every day via GitHub Actions
- You can manually trigger the workflow from the Actions tab

## Project Structure
- `bot/` — Autonomous bot logic (planner, executor, config, complexity checks)
- `src/` — Frontend code (React, TypeScript, styles)
- `.github/workflows/autobot.yml` — CI workflow for daily bot execution
- `bot/user_config.yaml` — User/project configuration

## License
MIT

---

*This project demonstrates autonomous, incremental software development using cloud-based bots and modern CI/CD workflows.*
