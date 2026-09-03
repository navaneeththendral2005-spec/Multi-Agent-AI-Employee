from pathlib import Path


class FileEditor:
    """
    Controlled file editor for generated software projects.

    Allows the AI system to:
    - Read project files
    - Replace file contents
    - Create files
    - Prevent edits outside the project directory
    """

    def __init__(self, project_path: str):
        self.project_path = Path(
            project_path
        ).resolve()

        if not self.project_path.exists():
            raise FileNotFoundError(
                f"Project directory not found: "
                f"{project_path}"
            )

    # -----------------------------------------------------
    # SAFE PATH HANDLING
    # -----------------------------------------------------

    def _safe_path(self, file_path: str) -> Path:
        """
        Ensure the requested file remains inside
        the generated project directory.
        """

        path = (
            self.project_path / file_path
        ).resolve()

        try:
            path.relative_to(
                self.project_path
            )

        except ValueError:

            raise PermissionError(
                "File access outside the generated "
                "project is not allowed."
            )

        return path

    # -----------------------------------------------------
    # READ FILE
    # -----------------------------------------------------

    def read_file(
        self,
        file_path: str
    ) -> str:
        """
        Read a project file.
        """

        path = self._safe_path(
            file_path
        )

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Not a file: {file_path}"
            )

        return path.read_text(
            encoding="utf-8"
        )

    # -----------------------------------------------------
    # WRITE FILE
    # -----------------------------------------------------

    def write_file(
        self,
        file_path: str,
        content: str
    ) -> str:
        """
        Create or replace a project file.
        """

        path = self._safe_path(
            file_path
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        path.write_text(
            content,
            encoding="utf-8"
        )

        return str(
            path.relative_to(
                self.project_path
            )
        )

    # -----------------------------------------------------
    # CHECK FILE
    # -----------------------------------------------------

    def file_exists(
        self,
        file_path: str
    ) -> bool:
        """
        Check whether a project file exists.
        """

        path = self._safe_path(
            file_path
        )

        return (
            path.exists()
            and path.is_file()
        )