from code_file_parser import CodeFileParser
from workspace_manager import WorkspaceManager


class ProjectBuilder:
    """
    Converts AI-generated code into actual project files.
    """

    def __init__(self, project_name: str):
        self.project_name = project_name

        self.workspace = WorkspaceManager()
        self.parser = CodeFileParser()

    def build(self, generated_output: str):
        """
        Parse generated code and create the files
        inside the project workspace.
        """

        files = self.parser.parse(generated_output)

        if not files:
            raise ValueError(
                "No valid files were found in the "
                "Code Generator output."
            )

        created_files = []

        for file_path, content in files.items():

            project_path = (
                f"{self.project_name}/{file_path}"
            )

            self.workspace.write_file(
                project_path,
                content
            )

            created_files.append(project_path)

        return created_files