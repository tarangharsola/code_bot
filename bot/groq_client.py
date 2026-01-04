import json
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Optional

import requests


@dataclass(frozen=True)
class GroqResponse:
    text: str
    raw: dict[str, Any]


class GroqError(RuntimeError):
    pass


def _extract_json_object(text: str) -> str:
    """Extract a JSON object from model text.

    Accepts raw JSON or fenced ```json blocks.
    """
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()

    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        return stripped[start : end + 1].strip()

    raise GroqError("Model did not return a JSON object")


def generate_content(
    *,
    api_key: str,
    model: str,
    prompt: str,
    temperature: float = 0.2,
    timeout_seconds: int = 60,
    max_retries: int = 4,
) -> GroqResponse:
    """Call Groq (OpenAI-compatible Chat Completions API)."""
    if not api_key:
        raise GroqError("Missing Groq API key")
    model = (model or "").strip()
    if not model:
        raise GroqError("Missing Groq model")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        # Keep output bounded; large generations burn quota quickly.
        "max_tokens": 4096,
    }

    last_error: Optional[str] = None
    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
        except requests.RequestException as e:
            last_error = str(e)
            resp = None

        if resp is None:
            if attempt < max_retries:
                time.sleep(min(30, 2 ** (attempt + 1)))
                continue
            raise GroqError(f"Groq request failed: {last_error}")

        if resp.status_code in (429, 500, 502, 503, 504):
            body_preview = resp.text[:500]
            last_error = f"HTTP {resp.status_code}: {body_preview[:200]}"
            if attempt < max_retries:
                retry_after = resp.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    time.sleep(min(60, int(retry_after)))
                else:
                    time.sleep(min(60, 2 ** (attempt + 1)))
                continue
            raise GroqError(f"Groq transient failure: {last_error}")

        if resp.status_code >= 400:
            raise GroqError(f"Groq HTTP {resp.status_code}: {resp.text[:500]}")

        data = resp.json() or {}
        choices = data.get("choices") or []
        if not isinstance(choices, list) or not choices:
            raise GroqError("Groq returned no choices")

        message = choices[0].get("message") if isinstance(choices[0], dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, str) or not content.strip():
            raise GroqError("Groq returned empty output")

        return GroqResponse(text=content, raw=data)

    raise GroqError("Groq request failed")


def generate_json(
    *,
    api_key: str,
    model: str,
    prompt: str,
    temperature: float = 0.2,
    timeout_seconds: int = 60,
) -> dict[str, Any]:
    resp = generate_content(
        api_key=api_key,
        model=model,
        prompt=prompt,
        temperature=temperature,
        timeout_seconds=timeout_seconds,
    )
    json_text = _extract_json_object(resp.text)
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        raise GroqError(f"Failed to parse JSON from Groq: {e}") from e


def get_api_key_from_env(env_name: str = "GROQ_API_KEY") -> str:
    return (os.environ.get(env_name) or "").strip()
