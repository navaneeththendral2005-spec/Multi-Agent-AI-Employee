from models.llm_factory import get_llm


class ManagerAgent:
    """
    Manager Agent for the Multi-Agent AI Employee.

    The Manager Agent analyzes a software requirement
    and produces a concise development plan.
    """

    def __init__(self, provider: str = "gemini"):
        self.provider = provider
        self.llm = get_llm(provider)

    def run(self, request: str) -> str:
        """
        Analyze the user's software requirement and
        generate a concise, professional development plan.
        """

        prompt = f"""
You are the Manager Agent in a professional
multi-agent software development team.

Analyze the user's software requirement and create
a SHORT and PRACTICAL development plan.

IMPORTANT OUTPUT RULES:
- Do NOT write code.
- Do NOT write an introduction or conclusion.
- Do NOT add information outside the requested sections.
- Do NOT use Markdown headings such as ###.
- Do NOT use horizontal lines such as ---.
- Do NOT add "Expected Final System".
- Do NOT add "Ready to commence".
- Do NOT repeat the user's requirement unnecessarily.
- Keep the entire response below 400 words.
- Use short bullet points.
- Keep the output easy to read in a terminal.

Use EXACTLY this structure:

REQUIREMENT
<one or two sentences describing what needs to be built>

CORE FEATURES
• <feature>
• <feature>
• <feature>
• <feature>
• <feature>

DEVELOPMENT TASKS
1. <task>
2. <task>
3. <task>
4. <task>
5. <task>

RECOMMENDED AGENTS
• <agent> — <responsibility>
• <agent> — <responsibility>
• <agent> — <responsibility>
• <agent> — <responsibility>

WORKFLOW
<short workflow using arrows, for example:
Manager → Database → Backend → Frontend → Testing>

USER REQUIREMENT:
{request}
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