from agents.base_agent import BaseAgent
import json


class ManagerAgent(BaseAgent):
    """
    Manager Agent for CHORUS.

    Responsibilities:
    - Understand the user's request.
    - Use relevant conversation history.
    - Select the required agents.
    - Assign tasks.
    - Identify dependencies.
    - Generate a final response only when synthesis
      is actually required.
    """

    def __init__(self, provider: str = "gemini"):
        super().__init__("manager", provider)

    # =========================================================
    # MANAGER PLANNING
    # =========================================================

    def run(
        self,
        request: str,
        history: list | None = None
    ) -> dict:
        """
        Analyze the user's request and create a structured
        execution plan for the Orchestrator.
        """

        if history is None:
            history = []

        # -----------------------------------------------------
        # BUILD CONVERSATION CONTEXT
        # -----------------------------------------------------

        conversation_context = ""

        if history:

            history_lines = []

            for item in history:

                if not isinstance(item, dict):
                    continue

                role = str(
                    item.get("role", "")
                ).lower().strip()

                content = str(
                    item.get("content", "")
                ).strip()

                if not content:
                    continue

                if role == "user":
                    speaker = "USER"
                else:
                    speaker = "CHORUS"

                history_lines.append(
                    f"{speaker}: {content}"
                )

            if history_lines:

                conversation_context = (
                    "\n\nCONVERSATION HISTORY:\n\n"
                    + "\n".join(history_lines)
                )

        # -----------------------------------------------------
        # MANAGER PROMPT
        # -----------------------------------------------------

        prompt = f"""
You are the Manager Agent of CHORUS,
a professional multi-agent AI Employee.

Understand the user's request and select ONLY
the specialized agents actually required.

AVAILABLE AGENTS:

- developer
  Software development and programming.

- backend
  Backend architecture, APIs, databases,
  and server-side implementation.

- code_generator
  Generates actual source-code files.

- research
  Web research, information gathering,
  fact finding, and current information.

- content
  Articles, reports, summaries, documentation,
  and written content.

- data
  Data analysis, datasets, statistics,
  and data visualization.

- document
  Creating and managing documents and files.

- communication
  Gmail emails, email replies, messages,
  announcements, and communication tasks.

- tester
  Testing, syntax checking, failures,
  and test reports.

- debugger
  Root-cause analysis of software failures.

- code_reviewer
  Code quality, security, correctness,
  maintainability, and architecture review.

- code_fixer
  Fixing software issues and applying patches.


IMPORTANT RULES:

1. Select ONLY agents actually required.

2. Do NOT assign unrelated agents.

3. Give every selected agent a specific task.

4. Independent tasks must have:
   "depends_on": []

5. Create dependencies only when genuinely required.

6. Do NOT perform the task yourself.

7. Return ONLY valid JSON.

8. Do not use Markdown.

9. Do not include explanations outside the JSON.

10. For software development, code generation must happen
    before testing.

11. Testing must happen after code generation.

12. Do NOT assign debugger or code_fixer as part of the
    initial software-development execution plan.

13. If the initial test fails, the Orchestrator will
    dynamically run debugger followed by code_fixer and
    then run testing again.

14. Code review must happen only after successful
    final testing..

15. Do not assign tester, debugger, or code_fixer
    to unrelated tasks.

16. Avoid unnecessary multi-agent workflows.

17. If ONE specialized agent can completely handle
    the request, assign ONLY that agent.

18. Conversation history may be used when it helps
    understand the current request.

19. The current request always has priority.

20. Ignore unrelated conversation history.

21. Do not create dependencies for conditional recovery
    tasks such as debugger or code_fixer.

22. For software-development requests, the initial plan
    should contain only the tasks required to begin and
    validate the implementation. Failure-recovery tasks
    are handled by the Orchestrator.


RETURN EXACTLY:

{{
    "request": "<short description>",
    "tasks": [
        {{
            "id": "task_1",
            "agent": "<agent name>",
            "task": "<specific task>",
            "depends_on": []
        }}
    ]
}}

{conversation_context}

CURRENT USER REQUEST:

{request}
"""

        # -----------------------------------------------------
        # INVOKE MANAGER
        # -----------------------------------------------------

        response = self.invoke(
            prompt
        )

        content = response.content

        # -----------------------------------------------------
        # NORMALIZE RESPONSE
        # -----------------------------------------------------

        if isinstance(content, list):

            text_parts = []

            for item in content:

                if (
                    isinstance(item, dict)
                    and "text" in item
                ):
                    text_parts.append(
                        item["text"]
                    )

                elif isinstance(item, str):
                    text_parts.append(
                        item
                    )

            content = "\n".join(
                text_parts
            )

        content = str(
            content
        ).strip()

        # -----------------------------------------------------
        # REMOVE CODE FENCES
        # -----------------------------------------------------

        if content.startswith("```"):

            content = content.replace(
                "```json",
                ""
            )

            content = content.replace(
                "```",
                ""

            )

            content = content.strip()

        # -----------------------------------------------------
        # PARSE JSON
        # -----------------------------------------------------

        try:

            plan = json.loads(
                content
            )

        except json.JSONDecodeError as error:

            raise ValueError(
                "Manager Agent returned invalid JSON: "
                f"{error}"
            )

        # -----------------------------------------------------
        # VALIDATE PLAN
        # -----------------------------------------------------

        if "tasks" not in plan:

            raise ValueError(
                "Manager Agent response does not "
                "contain 'tasks'."
            )

        if not isinstance(
            plan["tasks"],
            list
        ):

            raise ValueError(
                "Manager Agent 'tasks' "
                "must be a list."
            )

        if not plan["tasks"]:

            raise ValueError(
                "Manager Agent returned an empty task list."
            )

        return plan

    # =========================================================
    # FINAL RESPONSE
    # =========================================================

    def create_final_response(
        self,
        request: str,
        results: dict
    ) -> str:
        """
        Synthesize multiple agent results into one
        final user-facing response.

        This should only be called when multiple
        results genuinely need to be combined.
        """

        formatted_results = []

        for task_id, result in results.items():

            formatted_results.append(
                f"""
TASK: {task_id}

RESULT:
{result}
"""
            )

        results_text = "\n".join(
            formatted_results
        )

        prompt = f"""
You are the Manager Agent of CHORUS.

The user's request was:

{request}

The specialized agents produced these results:

{results_text}

Create one concise, useful final response.

IMPORTANT:

- Directly answer the user's request.
- Combine relevant results.
- Do not mention task IDs.
- Do not mention orchestration.
- Do not mention internal architecture.
- Do not repeat information.
- Do not invent information.
- Keep the response concise.
- Return ONLY the final user-facing response.

FINAL RESPONSE:
"""

        response = self.invoke(
            prompt
        )

        content = response.content

        # -----------------------------------------------------
        # NORMALIZE RESPONSE
        # -----------------------------------------------------

        if isinstance(content, list):

            text_parts = []

            for item in content:

                if (
                    isinstance(item, dict)
                    and "text" in item
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