from pathlib import Path

from agents.base_agent import BaseAgent


class CodeReviewerAgent(BaseAgent):
    """
    Code Reviewer Agent for CHORUS.

    Reviews generated software projects for correctness,
    security, architecture, maintainability, and
    engineering quality.
    """

    def __init__(
        self,
        provider: str = "groq"
    ):
        super().__init__(
            "code_reviewer",
            provider
        )

    # =========================================================
    # CODE REVIEW
    # =========================================================

    def run(
        self,
        task: str
    ) -> str:
        """
        Review the generated project and produce a
        structured code review.
        """

        project_path = self._find_project_path(
            task
        )

        # -----------------------------------------------------
        # COLLECT PROJECT FILES
        # -----------------------------------------------------

        project_files = self._collect_project_files(
            project_path
        )

        if project_files:

            review_context = "\n\n".join(
                f"FILE: {file_path}\n{content}"
                for file_path, content
                in project_files.items()
            )

        else:

            review_context = (
                "No project source files were found."
            )

        # -----------------------------------------------------
        # REVIEW PROMPT
        # -----------------------------------------------------

        prompt = f"""
You are the Code Reviewer Agent in CHORUS,
a professional multi-agent software development system.

Your responsibility is to review the actual generated
source code and identify meaningful engineering issues.

PROJECT PATH:

{project_path or "Not provided"}

ASSIGNED TASK:

{task}

PROJECT SOURCE CODE:

{review_context}

IMPORTANT RULES:

1. Review ONLY the source code actually provided.
2. Do not invent files, vulnerabilities, or problems.
3. Do not claim that code was executed.
4. Do not claim that tests passed unless explicit
   test results confirm it.
5. Focus on meaningful issues rather than stylistic
   nitpicking.
6. Prioritize security and correctness problems.
7. Identify architectural problems when applicable.
8. Check for duplicated or unnecessarily complex logic.
9. Check error handling.
10. Check maintainability.
11. Check obvious security vulnerabilities.
12. Check dependencies and configuration.
13. Check testing coverage or obvious testing gaps.
14. Consider performance and scalability where relevant.
15. Do not modify files.
16. Do not rewrite the project.
17. Provide actionable recommendations.

REVIEW AREAS:

- Correctness
- Security
- Architecture
- Code quality
- Maintainability
- Error handling
- Performance
- Dependencies
- Configuration
- Testing
- Scalability

RETURN EXACTLY:

REVIEW STATUS
<APPROVED / CHANGES REQUIRED>

SUMMARY
<short overall assessment>

CRITICAL ISSUES
• <issue or "None identified">

HIGH PRIORITY ISSUES
• <issue or "None identified">

MEDIUM PRIORITY ISSUES
• <issue or "None identified">

LOW PRIORITY ISSUES
• <issue or "None identified">

SECURITY REVIEW
• <finding>
• <finding>

CODE QUALITY
• <finding>
• <finding>

ARCHITECTURE
• <finding>
• <finding>

RECOMMENDED CHANGES
1. <change>
2. <change>
3. <change>

FINAL RECOMMENDATION
<approve the project or explain what should be
addressed before approval>
"""

        # -----------------------------------------------------
        # INVOKE REVIEWER
        # -----------------------------------------------------

        try:

            response = self.invoke(
                prompt
            )

        except Exception as error:

            return (
                "CODE REVIEW FAILED\n\n"
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

        Falls back to CHORUS's default project directory.
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

    # =========================================================
    # COLLECT SOURCE FILES
    # =========================================================

    @staticmethod
    def _collect_project_files(
        project_path: str
    ) -> dict:
        """
        Collect relevant source files while ignoring
        environments, caches, and build directories.
        """

        if not project_path:
            return {}

        project = Path(
            project_path
        )

        if (
            not project.exists()
            or not project.is_dir()
        ):
            return {}

        supported_extensions = {
            ".py",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".java",
            ".cpp",
            ".c",
            ".cs",
            ".go",
            ".rs",
            ".html",
            ".css",
            ".json",
            ".yaml",
            ".yml",
        }

        ignored_directories = {
            ".git",
            ".venv",
            "venv",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
            "dist",
            "build",
        }

        files = {}

        for file_path in project.rglob("*"):

            if not file_path.is_file():
                continue

            if (
                file_path.suffix.lower()
                not in supported_extensions
            ):
                continue

            if any(
                directory in file_path.parts
                for directory in ignored_directories
            ):
                continue

            try:

                content = file_path.read_text(
                    encoding="utf-8"
                )

                relative_path = (
                    file_path.relative_to(
                        project
                    )
                )

                files[
                    str(relative_path)
                ] = content

            except (
                UnicodeDecodeError,
                OSError,
            ):

                continue

        return files