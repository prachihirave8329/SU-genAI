
import logging
import os
import time
from collections import OrderedDict
from threading import Lock

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Cache configuration
CACHE_MAX_ENTRIES = 128
CACHE_TTL_SECONDS = float(
    os.getenv("LLM_CACHE_TTL_SECONDS", "300")
)

# Cache format:
# {
#     cache_key: (expiry_timestamp, response_content)
# }
_response_cache = OrderedDict()
_cache_lock = Lock()


def _token_count(usage, *field_names):
    """Read a token count from provider usage metadata."""

    if usage is None:
        return None

    for field in field_names:
        value = (
            usage.get(field)
            if isinstance(usage, dict)
            else getattr(usage, field, None)
        )

        if value is not None:
            try:
                return int(value)
            except (TypeError, ValueError):
                return None

    return None


def _extract_groq_usage(usage):
    """Extract token usage from Groq responses."""

    prompt = _token_count(usage, "prompt_tokens")
    completion = _token_count(usage, "completion_tokens")
    total = _token_count(usage, "total_tokens")

    if total is None and prompt is not None and completion is not None:
        total = prompt + completion

    return prompt, completion, total


def _extract_gemini_usage(usage):
    """Extract token usage from Gemini responses."""

    prompt = _token_count(usage, "prompt_token_count")
    completion = _token_count(usage, "candidates_token_count")
    total = _token_count(usage, "total_token_count")

    if total is None and prompt is not None and completion is not None:
        total = prompt + completion

    return prompt, completion, total


def _generate_groq(system_prompt, user_prompt, model):
    """Generate a response through Groq."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from .env")

    from groq import Groq

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    usage = _extract_groq_usage(response.usage)

    return content, usage


def _generate_gemini(system_prompt, user_prompt, model):
    """Generate a response through Gemini."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from .env")

    from google import genai

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=model,
        contents=user_prompt,
        config={
            "system_instruction": system_prompt,
            "response_mime_type": "application/json",
            "temperature": 0.2,
        },
    )

    content = response.text
    usage = _extract_gemini_usage(
        getattr(response, "usage_metadata", None)
    )

    return content, usage


def _log_request(
    provider,
    model,
    started_at,
    usage,
    cache_hit,
    outcome,
):
    """Log latency and token usage without logging user content."""

    latency_ms = (time.perf_counter() - started_at) * 1000

    prompt_tokens, completion_tokens, total_tokens = usage

    logger.info(
        "llm_request provider=%s model=%s latency_ms=%.2f "
        "prompt_tokens=%s completion_tokens=%s total_tokens=%s "
        "cache_hit=%s outcome=%s",
        provider,
        model,
        latency_ms,
        prompt_tokens,
        completion_tokens,
        total_tokens,
        cache_hit,
        outcome,
    )


def generate_response(system_prompt: str, user_prompt: str) -> str:
    """
    Generate an LLM response.

    Supports Groq and Gemini.

    Features:
    - Provider token usage tracking
    - Request latency logging
    - LRU cache with maximum 128 entries
    - Cache expiration after configured TTL
    - Does not cache failed or empty responses
    """

    provider = os.getenv("LLM_PROVIDER", "groq").lower()

    if provider == "groq":
        model = os.getenv(
            "GROQ_MODEL",
            "llama-3.3-70b-versatile",
        )

    elif provider == "gemini":
        model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash",
        )

    else:
        model = "unknown"

    cache_key = (
        provider,
        model,
        system_prompt,
        user_prompt,
    )

    started_at = time.perf_counter()

    # Check cache and remove expired entries.
    cached_response = None

    with _cache_lock:
        cached_entry = _response_cache.get(cache_key)

        if cached_entry is not None:
            expires_at, response_content = cached_entry

            if time.monotonic() >= expires_at:
                del _response_cache[cache_key]

            else:
                cached_response = response_content
                _response_cache.move_to_end(cache_key)

    # Return cached response if it has not expired.
    if cached_response is not None:
        _log_request(
            provider,
            model,
            started_at,
            (0, 0, 0),
            True,
            "success",
        )

        return cached_response

    try:
        # Generate response using selected provider.
        if provider == "groq":
            content, usage = _generate_groq(
                system_prompt,
                user_prompt,
                model,
            )

        elif provider == "gemini":
            content, usage = _generate_gemini(
                system_prompt,
                user_prompt,
                model,
            )

        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider}"
            )

        # Validate generated response.
        if not isinstance(content, str) or not content.strip():
            raise ValueError("LLM returned an empty response.")

        # Store successful response if caching is enabled.
        if CACHE_TTL_SECONDS > 0:
            with _cache_lock:
                _response_cache[cache_key] = (
                    time.monotonic() + CACHE_TTL_SECONDS,
                    content,
                )

                _response_cache.move_to_end(cache_key)

                # Remove oldest entries when cache is full.
                while len(_response_cache) > CACHE_MAX_ENTRIES:
                    _response_cache.popitem(last=False)

        # Log successful provider request.
        _log_request(
            provider,
            model,
            started_at,
            usage,
            False,
            "success",
        )

        return content

    except Exception:
        # Log failed provider request.
        _log_request(
            provider,
            model,
            started_at,
            (None, None, None),
            False,
            "error",
        )

        logger.exception("LLM request failed.")

        raise


def clear_response_cache():
    """Clear cached responses, primarily for testing."""

    with _cache_lock:
        _response_cache.clear()
