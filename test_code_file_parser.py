from code_file_parser import CodeFileParser


def main():

    generated_output = """
FILE: backend/main.py

<START OF FILE>
from fastapi import FastAPI

app = FastAPI()
<END OF FILE>

FILE: requirements.txt

<START OF FILE>
fastapi
uvicorn
<END OF FILE>
"""

    parser = CodeFileParser()

    files = parser.parse(generated_output)

    print("\n" + "=" * 60)
    print("CODE FILE PARSER TEST")
    print("=" * 60)

    for path, content in files.items():

        print(f"\nFILE: {path}")
        print("-" * 60)
        print(content)


if __name__ == "__main__":
    main()