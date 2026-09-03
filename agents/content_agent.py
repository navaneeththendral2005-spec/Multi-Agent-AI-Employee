from agents.base_agent import BaseAgent


class ContentAgent(BaseAgent):
    """
    Content Agent for CHORUS.

    Responsible for:
    - Creating written content
    - Rewriting and editing
    - Summarization
    - Matching requested tone and format
    """

    def __init__(
        self,
        provider: str = "gemini"
    ):
        super().__init__(
            "content",
            provider
        )

    # =========================================================
    # CONTENT GENERATION
    # =========================================================

    def run(
        self,
        task: str
    ) -> str:
        """
        Execute the assigned content task.
        """

        prompt = f"""
You are CHORUS's Content Agent.

Complete ONLY the content task below.

ASSIGNED TASK:
{task}

RULES:

1. Focus only on the assigned content task.
2. Follow the requested tone, length, format,
   and audience.
3. Use provided research or source information
   accurately.
4. Do not invent facts or unsupported information.
5. Do not perform coding, data analysis,
   or unrelated tasks.
6. Do not perform additional research unless
   explicitly requested.
7. Avoid unnecessary explanations.
8. Keep the output clear and well structured.
9. Return ONLY the requested content unless
   additional information is explicitly requested.

If source or research information is provided,
treat it as the factual basis for the response.
"""

        # -----------------------------------------------------
        # CENTRALIZED LLM HANDLER
        # -----------------------------------------------------

        response = self.invoke(
            prompt
        )

        # -----------------------------------------------------
        # NORMALIZE RESPONSE
        # -----------------------------------------------------

        content = response.content

        if isinstance(content, list):

            text_parts = []

            for item in content:

                if (
                    isinstance(item, dict)
                    and item.get("text")
                ):
                    text_parts.append(
                        item["text"]
                    )

                elif isinstance(item, str):
                    text_parts.append(
                        item
                    )

            return "\n".join(
                text_parts
            ).strip()

        return str(
            content
        ).strip()