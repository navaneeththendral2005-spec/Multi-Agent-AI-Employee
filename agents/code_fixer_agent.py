from pathlib import Path

from agents.base_agent import BaseAgent
from project_tools.file_editor import FileEditor


class CodeFixerAgent(BaseAgent):
    """
    Code Fixer Agent for CHORUS.

    Responsible for applying controlled fixes to generated
    software projects based on Debugger Agent findings.
    """

    def __init__(
        self,
        provider: str = "groq"
    ):
        super().__init__(
            "code_fixer",
            provider
        )

    # =========================================================
    # CODE FIXING
    # =========================================================

    def run(
        self,
        task: str
    ) -> str:

        project_path = self._find_project_path(
            task
        )

        if not project_path:

            return (
                "CODE FIX FAILED\n\n"
                "Generated project directory "
                "was not found."
            )

        try:

            editor = FileEditor(
                project_path
            )

        except Exception as error:

            return (
                "CODE FIX FAILED\n\n"
                "Unable to access project:\n"
                f"{error}"
            )

        project_files = self._collect_project_files(
            project_path
        )

        if not project_files:

            return (
                "CODE FIX FAILED\n\n"
                "No supported source files were found."
            )

        code_context = "\n\n".join(
            f"FILE: {file_path}\n{content}"
            for file_path, content
            in project_files.items()
        )

        prompt = f"""
You are the Code Fixer Agent in CHORUS,
a professional multi-agent software development system.

Your responsibility is to apply ONLY the fixes
identified by the Debugger Agent.

DEBUGGER REPORT:

{task}

PROJECT PATH:

{project_path}

PROJECT SOURCE CODE:

{code_context}

IMPORTANT RULES:

1. Fix ONLY the problems identified by the debugger.
2. Do not invent errors.
3. Do not rewrite the entire project unnecessarily.
4. Do not modify unrelated files.
5. Preserve existing functionality.
6. Preserve the existing architecture unless the
   debugger explicitly identifies an architectural issue.
7. Return COMPLETE replacement content for every
   file that must be modified.
8. Do not return partial files.
9. Do not use TODO placeholders.
10. Do not modify files outside the project.
11. Do not claim that tests passed.
12. Testing is performed separately by the Tester Agent.
13. Make the smallest safe change that resolves
    the identified problem.
14. Ensure imports and dependencies remain valid.
15. Only return files that actually need modification.
16. The FILE path must exactly match a file shown in
    PROJECT SOURCE CODE.
17. Do not use absolute paths.
18. Do not use Markdown code fences.

OUTPUT FORMAT:

FILE: relative/path/to/file.ext
<START OF FILE>
complete corrected file content
<END OF FILE>

FILE: another/relative/path.ext
<START OF FILE>
complete corrected file content
<END OF FILE>

Return one block for every modified file.

If no modification is required, return exactly:

NO FIX REQUIRED
"""

        # =====================================================
        # GENERATE FIX
        # =====================================================

        try:

            response = self.invoke(
                prompt
            )

        except Exception as error:

            return (
                "CODE FIX FAILED\n\n"
                f"LLM error: {error}"
            )

        # =====================================================
        # NORMALIZE RESPONSE
        # =====================================================

        content = self._normalize_response(
            response.content
        )

        if not content:

            return (
                "CODE FIX FAILED\n\n"
                "The Code Fixer returned an empty response."
            )

        # =====================================================
        # NO FIX REQUIRED
        # =====================================================

        if content.upper().strip().startswith(
            "NO FIX REQUIRED"
        ):

            return (
                "CODE FIXER\n\n"
                "No fix was required."
            )

        # =====================================================
        # PARSE FILE MODIFICATIONS
        # =====================================================

        fixes = self._parse_files(
            content
        )

        if not fixes:

            return (
                "CODE FIX FAILED\n\n"
                "The Code Fixer returned a response, "
                "but no valid file modifications could "
                "be parsed.\n\n"
                "EXPECTED FORMAT:\n"
                "FILE: relative/path/to/file.ext\n"
                "<START OF FILE>\n"
                "complete file content\n"
                "<END OF FILE>"
            )

        # =====================================================
        # VALIDATE ALL FIXES BEFORE WRITING ANY FILE
        # =====================================================

        validated_fixes = {}

        for file_path, file_content in fixes.items():

            try:

                safe_path = self._validate_file_path(
                    project_path,
                    file_path
                )

            except Exception as error:

                return (
                    "CODE FIX FAILED\n\n"
                    f"Invalid file path: {file_path}\n"
                    f"Error: {error}"
                )

            # -------------------------------------------------
            # ONLY MODIFY EXISTING PROJECT FILES
            # -------------------------------------------------

            normalized_path = str(
                Path(safe_path)
            )

            known_files = {
                str(Path(path))
                for path in project_files.keys()
            }

            if normalized_path not in known_files:

                return (
                    "CODE FIX FAILED\n\n"
                    f"Code Fixer attempted to modify "
                    f"a file that was not present in "
                    f"the project:\n{file_path}"
                )

            if not file_content.strip():

                return (
                    "CODE FIX FAILED\n\n"
                    f"Code Fixer returned empty content "
                    f"for:\n{file_path}"
                )

            validated_fixes[
                normalized_path
            ] = file_content

        # =====================================================
        # APPLY FIXES
        # =====================================================

        modified_files = []

        for file_path, file_content in (
            validated_fixes.items()
        ):

            try:

                editor.write_file(
                    file_path,
                    file_content
                )

                modified_files.append(
                    file_path
                )

            except Exception as error:

                return (
                    "CODE FIX FAILED\n\n"
                    f"File: {file_path}\n"
                    f"Error: {error}"
                )

        # =====================================================
        # RESULT
        # =====================================================

        if not modified_files:

            return (
                "CODE FIX FAILED\n\n"
                "No files were modified."
            )

        return (
            "CODE FIX COMPLETED\n\n"
            "MODIFIED FILES:\n"
            + "\n".join(
                f"• {file}"
                for file in modified_files
            )
        )

    # =========================================================
    # RESPONSE NORMALIZATION
    # =========================================================

    @staticmethod
    def _normalize_response(
        content
    ) -> str:
        """
        Normalize common LLM response formats.

        The fixer still requires structured file blocks,
        but harmless Markdown fences around the complete
        response are removed so provider formatting differences
        do not automatically cause a parsing failure.
        """

        if isinstance(
            content,
            list
        ):

            text_parts = []

            for item in content:

                if (
                    isinstance(item, dict)
                    and item.get("text")
                ):

                    text_parts.append(
                        str(
                            item["text"]
                        )
                    )

                elif isinstance(
                    item,
                    str
                ):

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
        # REMOVE OUTER MARKDOWN FENCES ONLY
        # -----------------------------------------------------

        lines = content.splitlines()

        if (
            len(lines) >= 2
            and lines[0].strip().startswith("```")
            and lines[-1].strip() == "```"
        ):

            content = "\n".join(
                lines[1:-1]
            ).strip()

        return content

    # =========================================================
    # PROJECT PATH
    # =========================================================

    @staticmethod
    def _find_project_path(
        task: str
    ):

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

        project = Path(
            project_path
        )

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

    # =========================================================
    # PATH SECURITY
    # =========================================================

    @staticmethod
    def _validate_file_path(
        project_path: str,
        file_path: str
    ) -> str:

        project = Path(
            project_path
        ).resolve()

        requested_path = Path(
            file_path
        )

        # -----------------------------------------------------
        # ABSOLUTE PATHS ARE NEVER ALLOWED
        # -----------------------------------------------------

        if requested_path.is_absolute():

            raise PermissionError(
                "Absolute file paths are not allowed."
            )

        requested = (
            project / requested_path
        ).resolve()

        try:

            relative = requested.relative_to(
                project
            )

        except ValueError:

            raise PermissionError(
                "Attempted to modify a file "
                "outside the generated project."
            )

        return str(
            relative
        )

    # =========================================================
    # PARSE FILES
    # =========================================================

    @staticmethod
    def _parse_files(
        content: str
    ) -> dict:
        """
        Parse structured Code Fixer output.

        The parser accepts minor whitespace differences but
        still requires explicit FILE / START / END markers.
        """

        files = {}

        current_file = None
        collecting = False
        buffer = []

        lines = content.splitlines()

        for line in lines:

            stripped = line.strip()

            # -------------------------------------------------
            # FILE HEADER
            # -------------------------------------------------

            if stripped.upper().startswith(
                "FILE:"
            ):

                # Save an unfinished block only if it has
                # explicit content and an active file.
                if (
                    current_file
                    and collecting
                    and buffer
                ):

                    files[
                        current_file
                    ] = "\n".join(
                        buffer
                    )

                current_file = (
                    stripped[
                        stripped.find(":") + 1:
                    ].strip()
                )

                buffer = []
                collecting = False

                continue

            # -------------------------------------------------
            # START OF FILE
            # -------------------------------------------------

            if stripped.upper() == (
                "<START OF FILE>"
            ):

                if not current_file:
                    continue

                buffer = []
                collecting = True

                continue

            # -------------------------------------------------
            # END OF FILE
            # -------------------------------------------------

            if stripped.upper() == (
                "<END OF FILE>"
            ):

                if current_file and collecting:

                    files[
                        current_file
                    ] = "\n".join(
                        buffer
                    )

                current_file = None
                collecting = False
                buffer = []

                continue

            # -------------------------------------------------
            # FILE CONTENT
            # -------------------------------------------------

            if collecting:

                buffer.append(
                    line
                )

        return files