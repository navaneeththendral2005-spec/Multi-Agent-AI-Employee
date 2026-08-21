import os

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm(provider: str = "gemini"):
    """
    Create an LLM based on the selected provider.

    Supported providers:
    - gemini
    - openai
    - anthropic
    """

    provider = provider.lower()

    if provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            temperature=0
        )

    if provider == "openai":
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-5.6"),
            temperature=0
        )

    if provider == "anthropic":
        return ChatAnthropic(
            model=os.getenv(
                "ANTHROPIC_MODEL",
                "claude-sonnet-4-6"
            ),
            temperature=0
        )

    raise ValueError(f"Unsupported LLM provider: {provider}")