from pathlib import Path


class WorkspaceManager:
    """
    Safely manages files inside the AI Employee workspace.

    Agents can use this class to create, read, update,
    and list project files without accessing files
    outside the workspace.
    """

    def __init__(self, workspace_dir: str = "workspace"):
        self.workspace_dir = Path(workspace_dir).resolve()

        # Create workspace if it doesn't exist
        self.workspace_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    # ---------------------------------------------------------
    # PATH SAFETY
    # ---------------------------------------------------------

    def _safe_path(self, relative_path: str) -> Path:
        """
        Convert a relative workspace path into a safe
        absolute path.

        Prevents agents from accessing files outside
        the workspace.
        """

        target = (
            self.workspace_dir / relative_path
        ).resolve()

        if not target.is_relative_to(
            self.workspace_dir
        ):
            raise ValueError(
                "Access denied: file must remain inside "
                "the workspace."
            )

        return target

    # ---------------------------------------------------------
    # CREATE / WRITE FILE
    # ---------------------------------------------------------

    def write_file(
        self,
        relative_path: str,
        content: str
    ):
        """
        Create a new file or overwrite an existing file.
        """

        file_path = self._safe_path(relative_path)

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path.write_text(
            content,
            encoding="utf-8"
        )

        return file_path

    # ---------------------------------------------------------
    # READ FILE
    # ---------------------------------------------------------

    def read_file(
        self,
        relative_path: str
    ) -> str:
        """
        Read a file from the workspace.
        """

        file_path = self._safe_path(relative_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"File not found: {relative_path}"
            )

        return file_path.read_text(
            encoding="utf-8"
        )

    # ---------------------------------------------------------
    # LIST FILES
    # ---------------------------------------------------------

    def list_files(self):
        """
        Return all files currently inside
        the workspace.
        """

        return [
            str(
                file.relative_to(
                    self.workspace_dir
                )
            )
            for file in self.workspace_dir.rglob("*")
            if file.is_file()
        ]

    # ---------------------------------------------------------
    # DELETE FILE
    # ---------------------------------------------------------

    def delete_file(
        self,
        relative_path: str
    ):
        """
        Delete a file from the workspace.
        """

        file_path = self._safe_path(relative_path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"File not found: {relative_path}"
            )

        file_path.unlink()

        return True