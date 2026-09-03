import subprocess
import sys
from pathlib import Path


def run_command(
    command: list[str],
    project_path: str,
    timeout: int = 60
) -> dict:
    """
    Run a command inside the generated project
    and capture its output.
    """

    project = Path(project_path)

    if not project.exists():
        raise FileNotFoundError(
            f"Project not found: {project_path}"
        )

    try:

        result = subprocess.run(
            command,
            cwd=project,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return {
            "command": " ".join(command),
            "return_code": result.returncode,
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }

    except subprocess.TimeoutExpired as error:

        return {
            "command": " ".join(command),
            "return_code": -1,
            "success": False,
            "stdout": (
                error.stdout.strip()
                if error.stdout
                else ""
            ),
            "stderr": (
                "Test execution timed out."
            )
        }

    except Exception as error:

        return {
            "command": " ".join(command),
            "return_code": -1,
            "success": False,
            "stdout": "",
            "stderr": str(error)
        }


def run_pytest(
    project_path: str,
    timeout: int = 60
) -> dict:
    """
    Run the project's pytest test suite.
    """

    return run_command(
        [
            sys.executable,
            "-m",
            "pytest"
        ],
        project_path,
        timeout
    )


def run_compile_check(
    project_path: str,
    timeout: int = 60
) -> dict:
    """
    Check Python files for syntax errors.
    """

    return run_command(
        [
            sys.executable,
            "-m",
            "compileall",
            "-q",
            "."
        ],
        project_path,
        timeout
    )


def _has_pytest_tests(
    project_path: str
) -> bool:
    """
    Check whether the project contains pytest test files.
    """

    project = Path(project_path)

    for file_path in project.rglob("*.py"):

        if not file_path.is_file():
            continue

        if any(
            directory in file_path.parts
            for directory in {
                ".git",
                ".venv",
                "venv",
                "node_modules",
                "__pycache__",
                ".pytest_cache",
            }
        ):
            continue

        if (
            file_path.name.startswith("test_")
            or file_path.name.endswith("_test.py")
        ):
            return True

    return False


def run_project_tests(
    project_path: str,
    timeout: int = 60
) -> dict:
    """
    Run the available tests for a generated project.

    Performs:
    1. Python syntax validation
    2. Pytest execution when pytest tests exist
    """

    results = {}

    # -----------------------------------------------------
    # SYNTAX CHECK
    # -----------------------------------------------------

    results["compile_check"] = run_compile_check(
        project_path,
        timeout
    )

    # -----------------------------------------------------
    # PYTEST
    # -----------------------------------------------------

    if _has_pytest_tests(project_path):

        results["pytest"] = run_pytest(
            project_path,
            timeout
        )

    else:

        results["pytest"] = {
            "command": "",
            "return_code": 0,
            "success": True,
            "stdout": "",
            "stderr": "",
            "status": "NOT RUN",
        }

    # -----------------------------------------------------
    # OVERALL STATUS
    # -----------------------------------------------------

    results["success"] = (
        results["compile_check"]["success"]
        and results["pytest"]["success"]
    )

    return results