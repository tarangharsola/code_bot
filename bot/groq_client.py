import json
import os
import re
import time
import ast
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
    base_payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Return only valid JSON. Do not include code fences, markdown, or commentary.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        # Keep output bounded; large generations burn quota quickly.
        "max_tokens": 4096,
    }

    # Some Groq models support OpenAI-style JSON mode.
    payloads_to_try: list[dict[str, Any]] = [
        {**base_payload, "response_format": {"type": "json_object"}},
        base_payload,
    ]

    last_error: Optional[str] = None
    for attempt in range(max_retries + 1):
        resp = None
        for payload in payloads_to_try:
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
            except requests.RequestException as e:
                last_error = str(e)
                resp = None
                continue

            # If JSON mode isn't supported, Groq typically returns 400.
            if resp.status_code == 400:
                body = (resp.text or "")[:500].lower()
                if "response_format" in body or "json_object" in body:
                    resp = None
                    continue
            break

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
    def _try_parse(text: str) -> dict[str, Any]:
        json_text = _extract_json_object(text)
        try:
            obj = json.loads(json_text)
            if not isinstance(obj, dict):
                raise GroqError("Groq JSON must be an object")
            return obj
        except json.JSONDecodeError:
            # Fallback: sometimes models emit Python dict-like output (single quotes).
            try:
                obj2 = ast.literal_eval(json_text)
            except Exception as e:
                raise GroqError(f"Failed to parse JSON from Groq: {e}") from e
            if not isinstance(obj2, dict):
                raise GroqError("Groq output was not a JSON object")
            return obj2

    resp = generate_content(
        api_key=api_key,
        model=model,
        prompt=prompt,
        temperature=temperature,
        timeout_seconds=timeout_seconds,
    )
    try:
        return _try_parse(resp.text)
    except GroqError:
        # One retry with a stricter instruction to return valid JSON only.
        retry_prompt = (
            prompt
            + "\n\nIMPORTANT: Your previous output was invalid JSON. "
            + "Return ONLY a valid JSON object using double quotes for all keys/strings."
        )
        resp2 = generate_content(
            api_key=api_key,
            model=model,
            prompt=retry_prompt,
            temperature=temperature,
            timeout_seconds=timeout_seconds,
        )
        return _try_parse(resp2.text)


def get_api_key_from_env(env_name: str = "GROQ_API_KEY") -> str:
    return (os.environ.get(env_name) or "").strip()
