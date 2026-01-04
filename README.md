# Autonomous Collaborative Code Editor Bot

This repository (`code_bot`) contains the automation (the bot + CI). The bot runs daily in GitHub Actions and **writes the actual application code into your target repository** (configured in `bot/user_config.yaml`, currently `tarangharsola/awesome-project`).

The end result is that **the whole web application lives in the target repo** — this repo only exists to run the self-operating developer bot.

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
- The bot lives in this repository (`code_bot`) and writes code into the target repo (`awesome-project`).
- Every day, the bot:
  1. Clones the target repo
  2. Plans 6 incremental improvements
  3. Applies changes, commits, and pushes

## Gemini (AI) setup

This bot can use Gemini to generate real code changes in the target repo.

- Add a repository secret in THIS bot repo:
   - `GEMINI_API_KEY`: your Gemini API key
- Add/verify the existing target repo secret in THIS bot repo:
   - `TARGET_REPO_PAT`: a GitHub Personal Access Token that can push to the target repo

Security notes:
- Do not paste API keys/tokens into chat or commit them to git.
- The workflow passes secrets via environment variables only.
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
- `.github/workflows/autobot.yml` — CI workflow for daily bot execution
- `bot/user_config.yaml` — Target repo + project prompt configuration

## License
MIT

---

*This project demonstrates autonomous, incremental software development using cloud-based bots and modern CI/CD workflows.*
