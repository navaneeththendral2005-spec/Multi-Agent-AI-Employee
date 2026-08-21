from dotenv import load_dotenv

from agents.code_generator_agent import CodeGeneratorAgent


def main():
    # Load environment variables from .env
    load_dotenv()

    generator = CodeGeneratorAgent(provider="gemini")

    technical_plan = """
    Build a simple student management backend.

    Technology Stack:
    - Python
    - FastAPI
    - SQLite

    Backend requirements:
    - Create student records
    - Retrieve students
    - Update students
    - Delete students
    - Provide REST API endpoints
    """

    print("\nGenerating code...\n")

    result = generator.run(technical_plan)

    print("=" * 60)
    print("CODE GENERATOR OUTPUT")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()