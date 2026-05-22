from __future__ import annotations

import json
import os
import re
from typing import Any

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency is listed, fallback keeps local dev resilient.
    def load_dotenv() -> bool:
        return False


load_dotenv()

DEFAULT_PROVIDER = "gemini"
DEFAULT_MODEL = "gemini-1.5-flash"
DEFAULT_TIMEOUT_SECONDS = 12


class LLMUnavailable(RuntimeError):
    """Raised when no usable LLM configuration is available."""


class LLMCallError(RuntimeError):
    """Raised when the LLM response cannot be safely used."""


def provider_name() -> str:
    return os.getenv("LABFIT_LLM_PROVIDER", DEFAULT_PROVIDER).strip().lower() or DEFAULT_PROVIDER


def model_name() -> str:
    return os.getenv("LABFIT_LLM_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def is_llm_available() -> bool:
    return provider_name() == "gemini" and bool(os.getenv("LABFIT_LLM_API_KEY", "").strip())


def call_llm_json(prompt: str) -> dict[str, Any]:
    if provider_name() != "gemini":
        raise LLMUnavailable("Configured LLM provider is not supported.")
    return call_gemini_json(prompt)


def call_gemini_json(prompt: str) -> dict[str, Any]:
    api_key = os.getenv("LABFIT_LLM_API_KEY", "").strip()
    if not api_key:
        raise LLMUnavailable("Gemini API key is not configured.")

    timeout = _timeout_seconds()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name()}:generateContent"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "Return only valid JSON. Do not include markdown fences, commentary, "
                            "or fields that are not supported by the provided evidence.\n\n"
                            f"{prompt}"
                        )
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
        },
    }

    try:
        response = requests.post(
            url,
            params={"key": api_key},
            json=payload,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise LLMCallError("Gemini request failed; using fallback.") from exc

    if response.status_code in {401, 403, 408, 409, 429} or response.status_code >= 500:
        raise LLMCallError(f"Gemini returned status {response.status_code}; using fallback.")
    if response.status_code >= 400:
        raise LLMCallError(f"Gemini request was not accepted ({response.status_code}); using fallback.")

    try:
        data = response.json()
    except ValueError as exc:
        raise LLMCallError("Gemini response was not JSON; using fallback.") from exc

    text = _extract_text(data)
    if not text:
        raise LLMCallError("Gemini response did not include text; using fallback.")
    try:
        return safe_parse_json(text)
    except ValueError as exc:
        raise LLMCallError("Gemini JSON parse failed; using fallback.") from exc


def safe_parse_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("No JSON object found in LLM response.")
        parsed = json.loads(cleaned[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("LLM response root must be a JSON object.")
    return parsed


def _extract_text(data: dict[str, Any]) -> str:
    candidates = data.get("candidates") or []
    if not candidates:
        return ""
    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    return "\n".join(str(part.get("text") or "") for part in parts).strip()


def _timeout_seconds() -> float:
    raw = os.getenv("LABFIT_LLM_TIMEOUT_SECONDS")
    if raw:
        try:
            return max(1.0, float(raw))
        except ValueError:
            return DEFAULT_TIMEOUT_SECONDS
    return DEFAULT_TIMEOUT_SECONDS
