## Step-by-Step Guide: How to Use This Bot

### 1. Fork or Clone This Repository
Clone this repo to your machine, or fork it to your own GitHub account if you want to run the bot in your own Actions environment.

### 2. Add Required Secrets in GitHub
Go to your repo → Settings → Secrets and variables → Actions, and add:
- `GROQ_API_KEY`: Your Groq API key (get it from https://console.groq.com/)
- `TARGET_REPO_PAT`: A GitHub Personal Access Token with push access to your target repo (the repo where you want the app built)

### 3. Configure the Bot
Edit `bot/user_config.yaml`:
- Set your GitHub username, the target repo, and the project prompt (what you want the bot to build)
- Optionally, set the Groq model (e.g., `llama-3-70b-8192` or `llama-3-8b-8192`)

### 4. (Optional) Run Locally for Testing
Install dependencies:
```sh
pip install -r requirements.txt
```
Set your secrets as environment variables:
```sh
$env:GROQ_API_KEY = "<your_groq_key>"
$env:TARGET_REPO_PAT = "<your_pat>"
python -m bot.main
```

### 5. Run in GitHub Actions (Cloud)
The bot runs automatically every day via the scheduled workflow, or you can trigger it manually from the Actions tab.

### 6. Check the Target Repo
After each run, check your target repo (as set in `bot/user_config.yaml`). The bot will push new commits with incremental improvements.

### 7. Troubleshooting
- If you see JSON errors, see the "Groq (AI) setup" and troubleshooting section above.
- If you see permission errors, make sure your PAT has push access to the target repo.
# Autonomous Collaborative Code Editor Bot

This repository (`code_bot`) contains the automation (the bot + CI). The bot runs daily in GitHub Actions and **writes the actual application code into your target repository** (configured in `bot/user_config.yaml`, currently `tarangharsola/awesome-project`).

The end result is that **the whole web application lives in the target repo** — this repo only exists to run the self-operating developer bot.

## Features
- **Collaborative Code Editor:** Real-time multi-user editing with syntax highlighting for JavaScript, Python, and HTML.
- **Live Cursors & User Presence:** See each user's cursor, name, and color. Active users panel displays all connected participants.
- **Document Sharing:** Unique shareable URLs for each coding session.
- **Responsive UI:** Clean, professional interface with dark mode and mobile/desktop support.
- **Robust Backend:** Uses WebSocket for real-time sync, CRDT/OT for conflict resolution, and production-grade error handling.
- **Autonomous Development:** Bot plans, implements, and commits incremental improvements every day for a configurable duration (including lifetime mode).
- **Cloud Execution:** Runs daily in GitHub Actions at 12:00 PM IST (06:30 UTC) and can be manually triggered.
- **Complexity & Performance Checks:** Ensures efficient, scalable code with every commit.

## How It Works
- The bot lives in this repository (`code_bot`) and writes code into the target repo (`awesome-project`).
- Every day, the bot:
  1. Clones the target repo
  2. Plans 6 incremental improvements
  3. Applies changes, commits, and pushes

Set `project_duration` in `bot/user_config.yaml` to:
- A positive integer for fixed number of days, or
- `lifetime` / `infinite` / `forever` / `unlimited` / `none` for no end date.

## Groq (AI) setup

This bot uses Groq (OpenAI-compatible API) to generate real code changes in the target repo.

**Required secrets in THIS bot repo:**
- `GROQ_API_KEY`: your Groq API key
- `TARGET_REPO_PAT`: a GitHub Personal Access Token that can push to the target repo

**Strict JSON output:**
- The bot expects the AI to return a single, valid JSON object (not Python dicts, not single quotes).
- If you see errors like `Failed to parse JSON from Groq`, it means the model returned invalid JSON (often with single quotes or trailing commas).
- The prompt is tuned to demand strict JSON, but if errors persist, try a different Groq model or adjust the prompt for stricter compliance.

**Troubleshooting:**
- If you get `Failed to parse JSON from Groq: Expecting property name enclosed in double quotes`, the AI response was not valid JSON. This is a common issue with LLMs—try rerunning, or use a model known for strict JSON compliance (like `llama-3-70b-8192` on Groq).

Security notes:
- Do not paste API keys/tokens into chat or commit them to git.
- The workflow passes secrets via environment variables only.
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

---

*This project demonstrates autonomous, incremental software development using cloud-based bots and modern CI/CD workflows.*
