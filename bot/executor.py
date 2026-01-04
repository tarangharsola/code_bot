import subprocess
import os
from urllib.parse import quote
import re

from bot.ai_protocol import parse_changeset, validate_size, ProtocolError
from bot.groq_client import generate_json, get_api_key_from_env, GroqError
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

    # Guardrail: GitHub PATs are typically much longer than 29 chars.
    # Classic tokens often start with 'ghp_' and fine-grained tokens start with 'github_pat_'.
    if len(token) < 35 or not (token.startswith("ghp_") or token.startswith("github_pat_")):
        raise RuntimeError(
            f"{token_name} does not look like a valid GitHub PAT. "
            f"Create a new token and paste the full value into the '{token_name}' secret. "
            f"Expected a token starting with 'ghp_' or 'github_pat_' (len >= 35)."
        )

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


def execute_plan(plan):
    clone_target_repo()
    cwd = os.getcwd()
    os.chdir("target_repo")
    try:
        for step in plan:
            action = step['action']
            # Each action is mapped to a function
            if action == "ai_step":
                ai_step(step)
            else:
                raise Exception(f"Unknown action: {action}")
            git_commit(step['description'])
        subprocess.run(["git", "push", "origin", "HEAD:main"], check=True)
    finally:
        os.chdir(cwd)

def _write_file(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def _delete_file(path: str) -> None:
    if os.path.isdir(path):
        return
    if os.path.exists(path):
        os.remove(path)


def _repo_snapshot(max_files: int = 200) -> str:
    """Lightweight repo context for the model (paths only)."""
    try:
        out = subprocess.run(
            ["git", "ls-files"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        files = [l.strip() for l in out.splitlines() if l.strip()]
    except Exception:
        files = []

    deny_prefixes = (
        "node_modules/",
        ".git/",
        "dist/",
        "build/",
        ".venv/",
    )
    filtered = [f for f in files if not f.startswith(deny_prefixes)]
    if len(filtered) > max_files:
        filtered = filtered[:max_files]
    return "\n".join(filtered)


def ai_step(step: dict) -> None:
    """Use Groq to generate a small changeset and apply it."""
    import re
    config = load_config()
    api_key = get_api_key_from_env(config.get("groq_api_key_env", "GROQ_API_KEY"))
    model = (config.get("groq_model") or "llama-3.1-8b-instant").strip()

    project_prompt = (config.get("project_prompt", "") or "").strip()
    # Keep prompts bounded to reduce token usage/quota burn.
    if len(project_prompt) > 3000:
        project_prompt = project_prompt[:3000].rstrip() + "\n\n(Truncated for brevity.)"
    task = (step.get("task") or step.get("description") or "").strip()
    if not task:
        raise RuntimeError("AI step missing task/description")

    snapshot = _repo_snapshot()

    # If any .tsx/.ts/.js/.jsx file is being written, demand strict code output.
    code_file_exts = (".tsx", ".ts", ".js", ".jsx")
    code_file_task = False
    if "writes" in step:
        code_file_task = any(str(w.get("path", "")).endswith(code_file_exts) for w in step["writes"] if isinstance(w, dict))
    if not code_file_task and any(ext in task for ext in code_file_exts):
        code_file_task = True

    prompt = f"""You are a senior full-stack engineer.

Repository goal:
{project_prompt}

Current repository file list (may be truncated):
{snapshot}

Task for this commit:
{task}

Return ONLY a single JSON object with this schema:
{{
  \"summary\": string,
  \"writes\": [{{\"path\": string, \"content\": string}}],
  \"deletes\": [string]
}}

Formatting requirements:
- Output must be STRICT JSON (double quotes for all keys/strings).
- Do not wrap in markdown/code fences.
- No trailing commas.
"""
    if code_file_task:
        prompt += (
            "- For any file ending in .tsx, .ts, .js, or .jsx, the 'content' value must be valid, complete, and properly formatted code for that file type.\n"
            "- Do NOT return code as a JSON string, not as a Python dict, and not as a markdown block.\n"
            "- The 'content' must be directly usable as a source file.\n"
            "- Example for .tsx: Start with 'import' or 'export', and include a valid React component.\n"
        )
    prompt += "\nRules:\n- Output must be production-quality and efficient (avoid unnecessary abstractions; prefer simple, fast solutions).\n- Prefer minimal dependencies. Do not introduce heavy frameworks unless clearly necessary.\n- Only write source/config/docs files. Do NOT add node_modules, lockfiles, or large vendor bundles.\n- Keep changes minimal and commit-scoped (small PR-sized changes).\n- Paths must be relative and must not contain '..'.\n- Prefer updating existing files over creating many new ones.\n- Avoid placeholder code and TODOs.\n"

    max_retries = 2
    for attempt in range(max_retries):
        try:
            obj = generate_json(api_key=api_key, model=model, prompt=prompt)
            changeset = parse_changeset(obj)
            validate_size(changeset)
            # Post-process: unwrap code if AI returned a JSON string for code files
            for w in changeset.writes:
                if w.path.endswith(code_file_exts):
                    code = w.content.strip()
                    # If code is a JSON string or not valid code, retry
                    if code.startswith('{') and code.endswith('}'):
                        code_match = re.search(r"```[a-zA-Z]*\\s*([\s\S]+?)```", code)
                        if code_match:
                            w.content = code_match.group(1).strip()
                        else:
                            if attempt < max_retries - 1:
                                prompt += "\nIMPORTANT: Your previous output for 'content' was a JSON string. Return ONLY valid code for the file, not JSON."
                                raise GroqError("AI returned JSON string for code file")
                    # Basic code validation: must start with import/export/component
                    elif not (code.startswith('import') or code.startswith('export') or 'function' in code or 'const' in code or 'class' in code):
                        if attempt < max_retries - 1:
                            prompt += "\nIMPORTANT: Your previous output for 'content' was not valid code. Return ONLY valid code for the file."
                            raise GroqError("AI returned invalid code for code file")
            break
        except (GroqError, ProtocolError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"AI generation failed: {e}") from e
            continue

    for p in changeset.deletes:
        _delete_file(p)
    for w in changeset.writes:
        _write_file(w.path, w.content)
