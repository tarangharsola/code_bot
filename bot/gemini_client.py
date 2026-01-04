import json
import os
import re
from dataclasses import dataclass
from typing import Any, Optional

import requests


@dataclass(frozen=True)
class GeminiResponse:
    text: str
    raw: dict[str, Any]


class GeminiError(RuntimeError):
    pass


def _extract_json_object(text: str) -> str:
    """Extract a JSON object from model text.

    Accepts raw JSON or fenced ```json blocks.
    """
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()

    # If it's already JSON-ish, return as-is.
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped

    # Last resort: attempt to find first { ... } block.
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        return stripped[start : end + 1].strip()

    raise GeminiError("Model did not return a JSON object")


def generate_content(
    *,
    api_key: str,
    model: str,
    prompt: str,
    temperature: float = 0.2,
    timeout_seconds: int = 60,
) -> GeminiResponse:
    """Call Gemini via Google Generative Language API.

    API key must be supplied via env (never print/log it).
    """
    if not api_key:
        raise GeminiError("Missing Gemini API key")
    if not model:
        raise GeminiError("Missing Gemini model")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 8192,
        },
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
    except requests.RequestException as e:
        raise GeminiError(f"Gemini request failed: {e}") from e

    if resp.status_code >= 400:
        raise GeminiError(f"Gemini HTTP {resp.status_code}: {resp.text[:500]}")

    data = resp.json()
    parts = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [])
    )
    text = "\n".join([p.get("text", "") for p in parts if isinstance(p, dict)])
    if not text.strip():
        raise GeminiError("Gemini returned empty output")

    return GeminiResponse(text=text, raw=data)


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
        raise GeminiError(f"Failed to parse JSON from Gemini: {e}") from e


def get_api_key_from_env(env_name: str = "GEMINI_API_KEY") -> str:
    return (os.environ.get(env_name) or "").strip()
