from abc import ABC, abstractmethod

from models.llm_factory import get_llm, invoke_with_retry


class BaseAgent(ABC):
    """
    Common base class for all CHORUS agents.

    Provides:
    - Agent name
    - LLM provider
    - LLM connection
    - Centralized retry and fallback handling
    - LLM usage tracking
    """

    def __init__(
        self,
        name: str,
        provider: str = "gemini"
    ):
        self.name = name
        self.provider = provider.lower().strip()

        # Create the primary LLM for this agent.
        self.llm = get_llm(
            self.provider
        )

    def invoke(
        self,
        prompt: str
    ):
        """
        Send a prompt through the centralized
        LLM retry/fallback system.
        """

        return invoke_with_retry(
            llm=self.llm,
            prompt=prompt,
            provider=self.provider,
            agent_name=self.name
        )

    @abstractmethod
    def run(
        self,
        task: str
    ) -> str:
        """
        Execute the assigned task and return
        the agent's result.
        """
        pass
