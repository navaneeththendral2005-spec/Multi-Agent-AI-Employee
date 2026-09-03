from pathlib import Path

from agents.base_agent import BaseAgent
from project_tools.file_editor import FileEditor


class CodeGeneratorAgent(BaseAgent):
    """
    Code Generator Agent for CHORUS.

    Responsible for generating actual source-code files
    and saving them into the generated project workspace.
    """

    def __init__(
        self,
        provider: str = "groq"
    ):
        super().__init__(
            "code_generator",
            provider
        )

    # =========================================================
    # CODE GENERATION
    # =========================================================

    def run(
        self,
        task: str
    ) -> str:
        """
        Generate source-code files and save them
        into the generated project directory.
        """

        # -----------------------------------------------------
        # PROJECT WORKSPACE
        # -----------------------------------------------------

        project_path = Path(
            "generated_project"
        )

        project_path.mkdir(
            parents=True,
            exist_ok=True
        )

        try:

            editor = FileEditor(
                str(project_path)
            )

        except Exception as error:

            return (
                "CODE GENERATION FAILED\n\n"
                "Unable to access project workspace:\n"
                f"{error}"
            )

        # -----------------------------------------------------
        # GENERATION PROMPT
        # -----------------------------------------------------

        prompt = f"""
You are the Code Generator Agent in CHORUS,
a professional multi-agent software development system.

ASSIGNED TASK:

{task}

Your responsibility is to generate the actual
source-code files required for this task.

RULES:

1. Generate complete and functional code.
2. Follow the technology requirements provided.
3. Create only the files required by the task.
4. Every file must have a clear relative path.
5. Include all required imports.
6. Ensure the generated files work together.
7. Keep the project modular and maintainable.
8. Do not use TODO placeholders.
9. Do not generate incomplete code.
10. Include tests when required by the task.
11. Include required configuration files when necessary.
12. Do not generate unnecessary documentation.
13. Do not perform debugging or code review.
14. Do not provide lengthy explanations.
15. Do not use Markdown code fences.

RETURN EVERY FILE EXACTLY LIKE THIS:

FILE: path/to/file.ext

<START OF FILE>
complete file content
<END OF FILE>

Generate every required file.
Do not omit important files.

ASSIGNED TASK:

{task}
"""

        # -----------------------------------------------------
        # GENERATE CODE
        # -----------------------------------------------------

        try:

            response = self.invoke(
                prompt
            )

        except Exception as error:

            return (
                "CODE GENERATION FAILED\n\n"
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

            content = "\n".join(
                text_parts
            )

        else:

            content = str(
                content
            )

        content = content.strip()

        # -----------------------------------------------------
        # PARSE GENERATED FILES
        # -----------------------------------------------------

        files = self._parse_files(
            content
        )

        if not files:

            return (
                "CODE GENERATION FAILED\n\n"
                "No valid source files were generated."
            )

        # -----------------------------------------------------
        # WRITE FILES
        # -----------------------------------------------------

        generated_files = []

        for file_path, file_content in files.items():

            try:

                safe_path = self._validate_file_path(
                    project_path,
                    file_path
                )

                editor.write_file(
                    safe_path,
                    file_content
                )

                generated_files.append(
                    safe_path
                )

            except Exception as error:

                return (
                    "CODE GENERATION FAILED\n\n"
                    f"File: {file_path}\n"
                    f"Error: {error}"
                )

        # -----------------------------------------------------
        # RESULT
        # -----------------------------------------------------

        return (
            "CODE GENERATION COMPLETED\n\n"
            "PROJECT DIRECTORY:\n"
            f"{project_path}\n\n"
            "GENERATED FILES:\n"
            + "\n".join(
                f"• {file}"
                for file in generated_files
            )
        )

    # =========================================================
    # FILE PARSER
    # =========================================================

    @staticmethod
    def _parse_files(
        content: str
    ) -> dict:
        """
        Parse generated file blocks from the LLM response.
        """

        files = {}

        current_file = None
        collecting = False
        buffer = []

        for line in content.splitlines():

            # -------------------------------------------------
            # NEW FILE
            # -------------------------------------------------

            if line.startswith("FILE:"):

                if current_file and buffer:

                    files[current_file] = (
                        "\n".join(
                            buffer
                        ).strip()
                    )

                current_file = (
                    line.replace(
                        "FILE:",
                        "",
                        1
                    ).strip()
                )

                buffer = []
                collecting = False

                continue

            # -------------------------------------------------
            # START FILE
            # -------------------------------------------------

            if line.strip() == "<START OF FILE>":

                buffer = []
                collecting = True

                continue

            # -------------------------------------------------
            # END FILE
            # -------------------------------------------------

            if line.strip() == "<END OF FILE>":

                if current_file:

                    files[current_file] = (
                        "\n".join(
                            buffer
                        ).strip()
                    )

                current_file = None
                buffer = []
                collecting = False

                continue

            # -------------------------------------------------
            # FILE CONTENT
            # -------------------------------------------------

            if collecting:

                buffer.append(
                    line
                )

        return files

    # =========================================================
    # PATH SECURITY
    # =========================================================

    @staticmethod
    def _validate_file_path(
        project_path: Path,
        file_path: str
    ) -> str:
        """
        Prevent generated files from escaping the
        generated project directory.
        """

        project = (
            project_path
            .resolve()
        )

        requested = (
            project / file_path
        ).resolve()

        try:

            requested.relative_to(
                project
            )

        except ValueError:

            raise PermissionError(
                "Generated file path attempts "
                "to escape the project directory."
            )

        return str(
            requested.relative_to(
                project
            )
        )