"""Small wrapper around the LLM. If no API key is set, returns None and the
callers fall back to built-in text, so the app always works offline."""
import logging

from app.config import get_settings

log = logging.getLogger(__name__)


def ask_llm(prompt: str, max_tokens: int = 200) -> str | None:
    settings = get_settings()
    if not settings.anthropic_api_key:
        return None
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        msg = client.messages.create(
            model=settings.llm_model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()
    except Exception as exc:  # never crash the request because of the LLM
        log.warning("LLM call failed: %s", exc)
        return None
