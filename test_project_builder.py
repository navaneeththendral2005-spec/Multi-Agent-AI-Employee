from project_builder import ProjectBuilder


def main():

    generated_output = """
FILE: backend/main.py

<START OF FILE>
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Student Management API"}
<END OF FILE>

FILE: requirements.txt

<START OF FILE>
fastapi
uvicorn
<END OF FILE>
"""

    builder = ProjectBuilder(
        "student_management"
    )

    created_files = builder.build(
        generated_output
    )

    print("\n" + "=" * 60)
    print("PROJECT BUILDER")
    print("=" * 60)

    print("\nCreated files:")

    for file_path in created_files:
        print(f"  ✓ {file_path}")

    print("\nProject successfully created.")


if __name__ == "__main__":
    main()