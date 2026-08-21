from models.llm_factory import get_llm


class BackendAgent:
    """
    Backend Agent for the Multi-Agent AI Employee.

    The Backend Agent is responsible for analyzing the
    technical plan and creating a backend implementation plan.
    """

    def __init__(self, provider: str = "gemini"):
        self.provider = provider
        self.llm = get_llm(provider)

    def run(self, developer_plan: str) -> str:
        """
        Convert the Developer Agent's technical plan
        into a backend-specific implementation plan.
        """

        prompt = f"""
You are the Backend Agent in a professional
multi-agent software development team.

The Developer Agent has created the following
technical implementation plan:

{developer_plan}

Your responsibility is to focus ONLY on the
backend development of this software.

IMPORTANT OUTPUT RULES:

- Do NOT write the complete application code yet.
- Do NOT discuss frontend development.
- Do NOT discuss UI/UX design.
- Do NOT add unnecessary explanations.
- Do NOT use Markdown headings such as ###.
- Do NOT use horizontal lines such as ---.
- Keep the response below 400 words.
- Use short bullet points.
- Keep the output practical and easy to read.

Use EXACTLY this structure:

BACKEND TECHNOLOGY
• Language: <language>
• Framework: <framework>
• Database: <database>
• API Style: <REST/GraphQL/etc.>

BACKEND ARCHITECTURE
• <component>
• <component>
• <component>
• <component>

DATABASE DESIGN
• <table/model>
• <table/model>
• <table/model>

API ENDPOINTS
• <HTTP method> <endpoint> — <purpose>
• <HTTP method> <endpoint> — <purpose>
• <HTTP method> <endpoint> — <purpose>
• <HTTP method> <endpoint> — <purpose>

BACKEND TASKS
1. <task>
2. <task>
3. <task>
4. <task>
5. <task>

DEPENDENCIES
• <dependency>
• <dependency>
• <dependency>

IMPLEMENTATION ORDER
1. <step>
2. <step>
3. <step>
4. <step>

Focus only on backend responsibilities.

DEVELOPER PLAN:
{developer_plan}
"""

        # Send request to the selected LLM
        response = self.llm.invoke(prompt)

        # Extract response content
        content = response.content

        # Gemini may return content as a list
        if isinstance(content, list):
            text_parts = []

            for item in content:
                if isinstance(item, dict) and "text" in item:
                    text_parts.append(item["text"])

                elif isinstance(item, str):
                    text_parts.append(item)

            return "\n".join(text_parts).strip()

        # Normal string response
        return str(content).strip()