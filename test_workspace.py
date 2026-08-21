from workspace_manager import WorkspaceManager


def main():
    workspace = WorkspaceManager()

    # Create a test file
    workspace.write_file(
        "test_project/hello.txt",
        "Hello from the Multi-Agent AI Employee!"
    )

    print("✓ File created")

    # Read the file
    content = workspace.read_file(
        "test_project/hello.txt"
    )

    print("✓ File read")
    print(f"Content: {content}")

    # List workspace files
    files = workspace.list_files()

    print("✓ Workspace files:")
    for file in files:
        print(f"  - {file}")


if __name__ == "__main__":
    main()