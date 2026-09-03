from pathlib import Path

from agents.base_agent import BaseAgent
from testing_tools.runner import run_project_tests


class TesterAgent(BaseAgent):
    """
    Tester Agent for CHORUS.

    Responsible for validating generated software projects
    using the actual testing tools and producing a concise
    structured test report.
    """

    def __init__(
        self,
        provider: str = "groq"
    ):
        super().__init__(
            "tester",
            provider
        )

    # =========================================================
    # TEST PROJECT
    # =========================================================

    def run(
        self,
        task: str
    ) -> str:
        """
        Run the actual project tests and interpret
        the resulting output.
        """

        # -----------------------------------------------------
        # FIND PROJECT
        # -----------------------------------------------------

        project_path = self._find_project_path(
            task
        )

        if not project_path:

            return (
                "TESTING FAILED\n\n"
                "No generated project directory "
                "was found."
            )

        # -----------------------------------------------------
        # RUN ACTUAL TESTS
        # -----------------------------------------------------

        try:

            test_results = run_project_tests(
                project_path
            )

        except Exception as error:

            return (
                "TESTING FAILED\n\n"
                f"Error: {error}"
            )

        # -----------------------------------------------------
        # NORMALIZE TEST RESULTS
        # -----------------------------------------------------

        result_text = str(
            test_results
        ).strip()

        if not result_text:

            return (
                "TESTING FAILED\n\n"
                "The testing tool returned "
                "no results."
            )

        # -----------------------------------------------------
        # TEST REPORT PROMPT
        # -----------------------------------------------------

        prompt = f"""
You are the Tester Agent in CHORUS,
a professional multi-agent software development system.

Your task is to analyze the ACTUAL testing-tool output
and produce an accurate test report.

ASSIGNED TASK:

{task}

PROJECT PATH:

{project_path}

ACTUAL TEST RESULTS:

{result_text}

IMPORTANT RULES:

1. Use ONLY the actual test results provided above.
2. Never invent test results.
3. Never claim PASS unless the actual results support it.
4. Clearly identify failed tests.
5. Identify syntax errors when present.
6. Identify pytest failures when present.
7. Preserve useful error messages for the Debugger Agent.
8. Distinguish warnings from actual failures.
9. Keep the report concise and practical.
10. Focus ONLY on software testing.
11. Do not modify any files.
12. Do not attempt to fix the project.
13. The overall TEST STATUS must be PASS only when
    the actual testing results indicate that the project
    successfully passed validation.

RETURN EXACTLY:

TEST STATUS
<PASS / FAIL>

SYNTAX CHECK
• Status: <PASS / FAIL / NOT RUN>
• Details: <details>

PYTEST
• Status: <PASS / FAIL / NOT RUN>
• Details: <details>

FAILURES
• <failure>
• <failure>

ERRORS
• <error>
• <error>

DEBUGGER INFORMATION
• <important information>
• <important information>

RECOMMENDATION
<what should happen next>
"""

        # -----------------------------------------------------
        # LLM INTERPRETATION
        # -----------------------------------------------------

        try:

            response = self.invoke(
                prompt
            )

        except Exception as error:

            return (
                "TESTING FAILED\n\n"
                "Unable to interpret test results.\n"
                f"LLM error: {error}\n\n"
                "RAW TEST RESULTS:\n"
                f"{result_text}"
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
        Find a project directory explicitly mentioned
        in the task.

        Falls back to CHORUS's default generated-project
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