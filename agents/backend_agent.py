from agents.base_agent import BaseAgent


class BackendAgent(BaseAgent):
    """
    Backend Agent for CHORUS.

    Responsible for backend architecture, APIs,
    databases, and server-side implementation planning.
    """

    def __init__(
        self,
        provider: str = "gemini"
    ):
        super().__init__(
            "backend",
            provider
        )

    # =========================================================
    # BACKEND PLANNING
    # =========================================================

    def run(
        self,
        task: str
    ) -> str:
        """
        Create a practical backend implementation plan
        for the assigned task.
        """

        prompt = f"""
You are CHORUS's Backend Agent.

Complete ONLY the backend-development task below.

ASSIGNED TASK:
{task}

RESPONSIBILITY:

Design the backend architecture and implementation
strategy required for the assigned task.

RULES:

1. Focus only on backend development.
2. Do not perform frontend, research, content,
   data-analysis, or unrelated tasks.
3. Do not write complete application code yet.
4. Keep the response practical and concise.
5. Choose technologies appropriate for the task.
6. Do not invent requirements.
7. Clearly identify APIs, data requirements,
   dependencies, and implementation order.

RETURN:

BACKEND TECHNOLOGY
• Language:
• Framework:
• Database:
• API Style:

BACKEND ARCHITECTURE
• <component>
• <component>
• <component>
• <component>

DATABASE DESIGN
• <table / collection>
• <field / relationship>
• <field / relationship>

API ENDPOINTS
• <method> <endpoint> — <purpose>
• <method> <endpoint> — <purpose>
• <method> <endpoint> — <purpose>

BACKEND TASKS
1. <task>
2. <task>
3. <task>
4. <task>
5. <task>

DEPENDENCIES
• <dependency>
• <dependency>

IMPLEMENTATION ORDER
1. <step>
2. <step>
3. <step>
4. <step>
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