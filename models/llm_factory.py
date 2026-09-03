
import os
from functools import lru_cache
from collections import defaultdict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI


# =========================================================
# PROVIDER CONFIGURATION
# =========================================================

PROVIDER_MODELS = {
    "gemini": os.getenv(
        "GEMINI_MODEL",
        "gemini-3.6-flash"
    ),

    "groq": os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-120b"
    ),

    "mistral": os.getenv(
        "MISTRAL_MODEL",
        "mistral-small-latest"
    ),
}


# =========================================================
# LLM USAGE TRACKING
# =========================================================

_LLM_USAGE = {
    "total_calls": 0,
    "providers": defaultdict(int),
    "agents": defaultdict(int),
}


def reset_llm_usage():
    """
    Reset LLM usage counters.
    """

    _LLM_USAGE["total_calls"] = 0
    _LLM_USAGE["providers"].clear()
    _LLM_USAGE["agents"].clear()


def _record_llm_call(
    provider: str,
    agent_name: str | None = None
):
    """
    Record one actual LLM invocation.
    """

    provider = provider.lower().strip()

    _LLM_USAGE["total_calls"] += 1

    _LLM_USAGE["providers"][
        provider
    ] += 1

    if agent_name:
        _LLM_USAGE["agents"][
            agent_name
        ] += 1

    agent_display = (
        agent_name
        if agent_name
        else "unknown"
    )

    print(
        f"[LLM] "
        f"{provider.upper()} "
        f"| Agent: {agent_display} "
        f"| Call #{_LLM_USAGE['total_calls']}"
    )


def get_llm_usage():
    """
    Return the current LLM usage statistics.
    """

    return {
        "total_calls": _LLM_USAGE[
            "total_calls"
        ],

        "providers": dict(
            _LLM_USAGE["providers"]
        ),

        "agents": dict(
            _LLM_USAGE["agents"]
        ),
    }


def print_llm_usage():
    """
    Print a human-readable LLM usage summary.
    """

    usage = get_llm_usage()

    print()
    print("=" * 64)
    print(" LLM USAGE")
    print("=" * 64)

    print(
        f"Total calls: "
        f"{usage['total_calls']}"
    )

    print()
    print("BY PROVIDER")

    if usage["providers"]:

        for provider, count in (
            usage["providers"].items()
        ):
            print(
                f"- {provider}: {count}"
            )

    else:
        print("- none")

    print()
    print("BY AGENT")

    if usage["agents"]:

        for agent, count in (
            usage["agents"].items()
        ):
            print(
                f"- {agent}: {count}"
            )

    else:
        print("- none")

    print("=" * 64)
    print()


# =========================================================
# LLM CREATION
# =========================================================

@lru_cache(maxsize=None)
def get_llm(
    provider: str = "gemini"
):
    """
    Create and cache an LLM instance for the
    selected provider.

    Supported providers:
    - gemini
    - groq
    - mistral
    """

    provider = provider.lower().strip()

    # -----------------------------------------------------
    # GEMINI
    # -----------------------------------------------------

    if provider == "gemini":

        return ChatGoogleGenerativeAI(
            model=PROVIDER_MODELS["gemini"],
            temperature=0,
        )

    # -----------------------------------------------------
    # GROQ
    # -----------------------------------------------------

    if provider == "groq":

        return ChatGroq(
            model=PROVIDER_MODELS["groq"],
            temperature=0,
        )

    # -----------------------------------------------------
    # MISTRAL
    # -----------------------------------------------------

    if provider == "mistral":

        return ChatMistralAI(
            model=PROVIDER_MODELS["mistral"],
            temperature=0,
        )

    raise ValueError(
        f"Unsupported LLM provider: {provider}"
    )


# =========================================================
# RATE-LIMIT / QUOTA DETECTION
# =========================================================

def _is_rate_limit_error(
    error: Exception
) -> bool:
    """
    Determine whether an exception is related to
    rate limits, quota exhaustion, or temporary
    resource exhaustion.
    """

    message = str(
        error
    ).lower()

    indicators = [
        "429",
        "rate limit",
        "rate_limit",
        "resource exhausted",
        "resource_exhausted",
        "quota",
        "too many requests",
        "requests per minute",
        "tokens per minute",
        "quota exceeded",
        "quota_exceeded",
    ]

    return any(
        indicator in message
        for indicator in indicators
    )


# =========================================================
# RETRY + FALLBACK
# =========================================================

def invoke_with_retry(
    llm,
    prompt: str,
    provider: str = "gemini",
    fallback_provider: str = "mistral",
    agent_name: str | None = None
):
    """
    Invoke the primary LLM.

    Behavior:

        Primary
           |
           | success
           ↓
        Response

           |
           | quota / rate limit
           ↓
        Fallback
           |
           ↓
        Response

    No additional retry loop is performed.
    """

    # =====================================================
    # PRIMARY PROVIDER
    # =====================================================

    try:

        _record_llm_call(
            provider,
            agent_name
        )

        return llm.invoke(
            prompt
        )

    except Exception as error:

        # -------------------------------------------------
        # NORMAL ERROR
        # -------------------------------------------------

        if not _is_rate_limit_error(
            error
        ):
            raise

        print()
        print(
            "[LLM] Primary provider "
            "rate-limited or quota exhausted."
        )

        print(
            "[LLM] Switching immediately "
            f"to {fallback_provider.upper()}..."
        )

    # =====================================================
    # FALLBACK PROVIDER
    # =====================================================

    try:

        fallback_llm = get_llm(
            fallback_provider
        )

        _record_llm_call(
            fallback_provider,
            agent_name
        )

        return fallback_llm.invoke(
            prompt
        )

    except Exception as fallback_error:

        print()
        print(
            "[LLM] Fallback provider failed."
        )

        print(
            f"[LLM] Fallback error: "
            f"{fallback_error}"
        )

        raise RuntimeError(
            "All configured LLM providers "
            "failed to process the request."
        ) from fallback_error
