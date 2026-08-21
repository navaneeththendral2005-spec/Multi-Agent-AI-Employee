from models.llm_factory import get_llm


class DeveloperAgent:
    """
    Developer Agent for the Multi-Agent AI Employee.

    The Developer Agent converts the Manager Agent's
    development plan into a practical technical plan.
    """

    def __init__(self, provider: str = "gemini"):
        self.provider = provider
        self.llm = get_llm(provider)

    def run(self, development_plan: str) -> str:
        """
        Convert the Manager Agent's plan into a concise
        technical implementation plan.
        """

        prompt = f"""
You are the Developer Agent in a professional
multi-agent software development team.

The Manager Agent has provided the following plan:

{development_plan}

Convert the Manager's plan into a SHORT and PRACTICAL
technical implementation plan.

IMPORTANT OUTPUT RULES:
- Do NOT write the actual application code.
- Do NOT write an introduction or conclusion.
- Do NOT add information outside the requested sections.
- Do NOT use Markdown headings such as ###.
- Do NOT use horizontal lines such as ---.
- Do NOT add "Expected Final System".
- Do NOT add "Ready to commence".
- Do NOT repeat the Manager's plan unnecessarily.
- Keep the entire response below 500 words.
- Use short bullet points.
- Keep the output easy to read in a terminal.

Use EXACTLY this structure:

TECHNOLOGY STACK
• Language: <language>
• Backend: <framework>
• Frontend: <framework>
• Database: <database>
• Testing: <testing tools>

PROJECT STRUCTURE
<show a simple folder structure using plain text>

BACKEND TASKS
1. <task>
2. <task>
3. <task>
4. <task>

FRONTEND TASKS
1. <task>
2. <task>
3. <task>
4. <task>

DATABASE TASKS
1. <task>
2. <task>
3. <task>

API REQUIREMENTS
• <endpoint or API requirement>
• <endpoint or API requirement>
• <endpoint or API requirement>

DEPENDENCIES
• <dependency>
• <dependency>
• <dependency>
• <dependency>

IMPLEMENTATION ORDER
1. <step>
2. <step>
3. <step>
4. <step>
5. <step>

TESTING
• <testing requirement>
• <testing requirement>
• <testing requirement>

MANAGER PLAN:
{development_plan}
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