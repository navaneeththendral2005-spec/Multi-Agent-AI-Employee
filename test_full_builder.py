from dotenv import load_dotenv

from agents.code_generator_agent import CodeGeneratorAgent
from project_builder import ProjectBuilder


def main():
    # Load Gemini API key
    load_dotenv()

    # Create Code Generator
    generator = CodeGeneratorAgent(
        provider="gemini"
    )

    # Give the Code Generator a small technical plan
    technical_plan = """
    Build a simple Student Management API.

    Technology Stack:
    - Python
    - FastAPI
    - SQLite

    Required features:
    - Create student
    - Get students
    - Update student
    - Delete student
    """

    print("\n" + "=" * 60)
    print("       AI CODE GENERATION & PROJECT BUILDER")
    print("=" * 60)

    # -----------------------------------------
    # STEP 1: GENERATE CODE
    # -----------------------------------------

    print("\n[1/2] Code Generator")
    print("-" * 60)
    print("Generating project files...")

    generated_output = generator.run(
        technical_plan
    )

    print("✓ Code generation completed.")

    # -----------------------------------------
    # STEP 2: BUILD PROJECT
    # -----------------------------------------

    print("\n[2/2] Project Builder")
    print("-" * 60)
    print("Creating project files...")

    builder = ProjectBuilder(
        "student_management"
    )

    created_files = builder.build(
        generated_output
    )

    print("✓ Project creation completed.")

    # -----------------------------------------
    # RESULT
    # -----------------------------------------

    print("\n" + "=" * 60)
    print("              PROJECT CREATED")
    print("=" * 60)

    print("\nCreated files:")

    for file_path in created_files:
        print(f"  ✓ {file_path}")

    print("\nSystem Status: READY")


if __name__ == "__main__":
    main()