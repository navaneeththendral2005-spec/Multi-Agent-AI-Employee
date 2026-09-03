from agents.base_agent import BaseAgent


class BrowserAgent(BaseAgent):
    """
    Browser Agent responsible for web-related tasks.

    Responsibilities:
    - Identify relevant websites
    - Plan web navigation
    - Analyze provided web content
    - Compare online information
    - Identify useful sources
    - Prepare browser actions
    """

    def __init__(self, provider: str = "gemini"):
        super().__init__("browser", provider)

    def run(self, task: str) -> str:
        """
        Execute the assigned browser-related task.
        """

        prompt = f"""
You are the Browser Agent in a professional
multi-agent AI Employee.

ASSIGNED TASK:

{task}

Your responsibility is to handle web and
browser-related tasks.

SUPPORTED TASKS:

- Finding relevant websites
- Identifying useful web resources
- Planning website navigation
- Extracting information from provided web content
- Comparing information from multiple websites
- Identifying pages relevant to a user's request
- Planning browser actions
- Preparing information for the Research Agent

IMPORTANT RULES:

1. Focus ONLY on the assigned browser task.
2. Do not perform another agent's responsibility.
3. Do not invent information from websites.
4. Do not claim that you visited a website unless
   actual browser/web tools were provided.
5. Do not fabricate URLs.
6. Clearly distinguish verified information from
   assumptions.
7. Do not log into accounts.
8. Do not enter passwords or sensitive information.
9. Do not submit forms without explicit authorization.
10. Do not make purchases or financial transactions.
11. Do not send messages or emails.
12. Do not perform irreversible actions.
13. Keep the result concise and practical.

If actual web access is not available, explain what
information or browser access would be required.

OUTPUT FORMAT:

BROWSER TASK
<short description of the task>

RELEVANT RESOURCES
• <resource if known>
• <resource if known>
• <resource if known>

NAVIGATION PLAN
1. <step>
2. <step>
3. <step>

INFORMATION FOUND
• <verified information>
• <verified information>

LIMITATIONS
<state what could not be verified>

IMPORTANT:
Never pretend that browser navigation or live web
access occurred when no browser tool was available.

ASSIGNED TASK:

{task}
"""

        response = self.invoke(prompt)

        content = response.content

        # -------------------------------------------------
        # HANDLE LIST RESPONSES
        # -------------------------------------------------

        if isinstance(content, list):

            text_parts = []

            for item in content:

                if isinstance(item, dict):

                    text = item.get("text")

                    if text:
                        text_parts.append(text)

                elif isinstance(item, str):

                    text_parts.append(item)

            return "\n".join(
                text_parts
            ).strip()

        return str(content).strip()