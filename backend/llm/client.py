"""The only door to an LLM. Every call is cached by a hash of (model, system, prompt, schema).

Swap providers by replacing `_call`. Without credentials, `available()` is False and callers
fall back to rules or templates.
"""

import hashlib
import json
import logging
import os

from django.conf import settings

from .models import LLMCache

log = logging.getLogger(__name__)


class LLMUnavailable(Exception):
    pass


_fake = None  # tests install a callable(model, system, prompt, schema) -> str


def use_fake(fn):
    """Route all calls to `fn` (tests, offline demos). Pass None to restore."""
    global _fake
    _fake = fn


def available() -> bool:
    if _fake is not None:
        return True
    return bool(settings.ANTHROPIC_API_KEY or os.environ.get("ANTHROPIC_AUTH_TOKEN"))


def _key(model, system, prompt, schema) -> str:
    blob = json.dumps([model, system, prompt, schema], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


def _call(model: str, system: str, prompt: str, schema: dict | None, max_tokens: int) -> str:
    if _fake is not None:
        return _fake(model, system, prompt, schema)
    import anthropic

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY or None)
    kwargs = {}
    if schema is not None:
        kwargs["output_config"] = {"format": {"type": "json_schema", "schema": schema}}
    try:
        response = client.messages.create(
            model=model, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": prompt}], **kwargs,
        )
    except anthropic.APIConnectionError as e:
        raise LLMUnavailable(f"network: {e}") from e
    except anthropic.AuthenticationError as e:
        raise LLMUnavailable("authentication failed") from e
    except anthropic.APIStatusError as e:
        raise LLMUnavailable(f"HTTP {e.status_code}: {e.message}") from e
    if response.stop_reason == "refusal":
        raise LLMUnavailable("refused")
    return next((b.text for b in response.content if b.type == "text"), "")


def complete(prompt: str, *, system: str = "", schema: dict | None = None,
             model: str | None = None, max_tokens: int = 2048, use_cache: bool = True) -> str:
    """Return the model's text (a JSON string when `schema` is given). Raises LLMUnavailable."""
    if not available():
        raise LLMUnavailable("no credentials configured")
    model = model or settings.LLM_MODEL_FAST
    key = _key(model, system, prompt, schema)
    if use_cache and _fake is None:
        hit = LLMCache.objects.filter(key=key).first()
        if hit:
            return hit.response
    text = _call(model, system, prompt, schema, max_tokens)
    if use_cache and _fake is None:
        LLMCache.objects.update_or_create(key=key, defaults={"model": model, "response": text})
    return text


def complete_json(prompt: str, *, schema: dict, **kw) -> dict:
    text = complete(prompt, schema=schema, **kw)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise LLMUnavailable(f"invalid JSON from model: {e}") from e
