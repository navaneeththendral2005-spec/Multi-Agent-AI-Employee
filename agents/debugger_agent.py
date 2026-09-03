from pathlib import Path

from agents.base_agent import BaseAgent


class DebuggerAgent(BaseAgent):
    """
    Debugger Agent for CHORUS.

    Responsible for analyzing test failures,
    identifying root causes, and providing precise
    guidance for the Code Fixer Agent.
    """

    def __init__(
        self,
        provider: str = "groq"
    ):
        super().__init__(
            "debugger",
            provider
        )

    # =========================================================
    # DEBUGGING
    # =========================================================

    def run(
        self,
        task: str
    ) -> str:
        """
        Analyze tester results and determine what needs
        to be fixed in the generated project.
        """

        project_path = self._find_project_path(
            task
        )

        prompt = f"""
You are the Debugger Agent in CHORUS,
a professional multi-agent software development system.

Your responsibility is to analyze actual software
test failures and determine how they should be fixed.

ASSIGNED TASK:

{task}

PROJECT PATH:

{project_path or "Not provided"}

IMPORTANT RULES:

1. Focus ONLY on debugging.
2. Analyze the provided test results carefully.
3. Identify the actual failure.
4. Identify the root cause of each failure.
5. Do not invent errors or failures.
6. Do not claim that a fix was applied.
7. Do not modify files.
8. Distinguish symptoms from root causes.
9. Identify affected files whenever possible.
10. Provide precise code-level guidance.
11. Prioritize critical failures first.
12. Do not unnecessarily rewrite working code.
13. Provide actionable instructions for the Code Fixer Agent.
14. Keep the report practical and concise.

RETURN EXACTLY:

DEBUG STATUS
<BUGS FOUND / NO BUGS FOUND>

FAILURE ANALYSIS
• <actual failure>
• <actual failure>

ROOT CAUSES
• <root cause>
• <root cause>

FILES INVOLVED
• <file>
• <file>

RECOMMENDED FIXES
1. <specific fix>
2. <specific fix>
3. <specific fix>

FIX PRIORITY
1. <highest priority>
2. <next priority>

VERIFICATION
• <test that should be run after the fix>
• <test that should be run after the fix>

Do not include information that cannot be supported
by the provided test results or project information.
"""

        # -----------------------------------------------------
        # INVOKE LLM
        # -----------------------------------------------------

        try:

            response = self.invoke(
                prompt
            )

        except Exception as error:

            return (
                "DEBUGGING FAILED\n\n"
                f"LLM error: {error}"
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

    # =========================================================
    # PROJECT PATH DETECTION
    # =========================================================

    @staticmethod
    def _find_project_path(
        task: str
    ):
        """
        Find the generated project directory mentioned
        in the task.

        Falls back to CHORUS's default generated project
        directory.
        """

        words = (
            task.replace('"', "")
            .replace("'", "")
            .split()
        )

        for word in words:

            path = Path(
                word
            )

            if (
                path.exists()
                and path.is_dir()
            ):

                return str(
                    path
                )

        # -----------------------------------------------------
        # DEFAULT PROJECT
        # -----------------------------------------------------

        default_path = Path(
            "generated_project"
        )

        if (
            default_path.exists()
            and default_path.is_dir()
        ):

            return str(
                default_path
            )

        return None