import json
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Optional

import requests


@dataclass(frozen=True)
class GeminiResponse:
    text: str
    raw: dict[str, Any]


class GeminiError(RuntimeError):
    pass


def _normalize_model(model: str) -> str:
    m = (model or "").strip()
    if not m:
        return m
    # Accept either "models/<name>" or "<name>".
    if m.startswith("models/"):
        return m[len("models/") :]
    return m


def list_models(*, api_key: str, timeout_seconds: int = 30) -> list[dict[str, Any]]:
    """List models available to this API key.

    Used to auto-recover from "model not found" errors.
    """
    if not api_key:
        raise GeminiError("Missing Gemini API key")
    url = "https://generativelanguage.googleapis.com/v1beta/models"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout_seconds)
    except requests.RequestException as e:
        raise GeminiError(f"ListModels request failed: {e}") from e
    if resp.status_code >= 400:
        raise GeminiError(f"ListModels HTTP {resp.status_code}: {resp.text[:500]}")
    data = resp.json() or {}
    models = data.get("models", [])
    return models if isinstance(models, list) else []


def _pick_fallback_model(models: list[dict[str, Any]]) -> Optional[str]:
    """Pick a model name (without 'models/' prefix) that supports generateContent."""
    candidates: list[str] = []
    for m in models:
        if not isinstance(m, dict):
            continue
        name = m.get("name")
        methods = m.get("supportedGenerationMethods") or []
        if not isinstance(name, str) or not isinstance(methods, list):
            continue
        if "generateContent" not in methods:
            continue
        # Name comes back as "models/<id>".
        model_id = _normalize_model(name)
        candidates.append(model_id)

    if not candidates:
        return None

    # Prefer flash, then pro, then anything else.
    preferred = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ]
    for p in preferred:
        for c in candidates:
            if p in c:
                return c

    return candidates[0]


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
    max_retries: int = 4,
) -> GeminiResponse:
    """Call Gemini via Google Generative Language API.

    API key must be supplied via env (never print/log it).
    """
    if not api_key:
        raise GeminiError("Missing Gemini API key")
    model = _normalize_model(model)
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

    last_error: Optional[str] = None
    did_model_fallback = False
    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
        except requests.RequestException as e:
            last_error = str(e)
            resp = None

        if resp is None:
            if attempt < max_retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise GeminiError(f"Gemini request failed: {last_error}")

        if resp.status_code in (429, 500, 502, 503, 504):
            body_preview = resp.text[:500]
            # If the account quota is exhausted, retries won't help.
            if resp.status_code == 429 and (
                "exceeded your current quota" in body_preview.lower()
                or "check your plan" in body_preview.lower()
                or "billing" in body_preview.lower()
            ):
                raise GeminiError(
                    "Gemini quota exceeded for this API key. "
                    "Enable billing/upgrade plan or use a key with available quota. "
                    f"Response: {body_preview}"
                )

            last_error = f"HTTP {resp.status_code}: {body_preview[:200]}"
            if attempt < max_retries:
                retry_after = resp.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    time.sleep(min(60, int(retry_after)))
                else:
                    time.sleep(min(60, 2 ** (attempt + 1)))
                continue
            raise GeminiError(f"Gemini transient failure: {last_error}")

        if resp.status_code == 404 and not did_model_fallback:
            # Model name/version mismatch is common across API versions / key entitlements.
            # Try to recover by listing models and selecting one that supports generateContent.
            try:
                available = list_models(api_key=api_key)
                fallback = _pick_fallback_model(available)
            except GeminiError:
                fallback = None
            if fallback and fallback != model:
                model = fallback
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
                did_model_fallback = True
                if attempt < max_retries:
                    time.sleep(0.5)
                    continue

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

    raise GeminiError("Gemini request failed")


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
