from models.llm_factory import get_llm


class CodeGeneratorAgent:
    """
    Code Generator Agent for the Multi-Agent AI Employee.

    Converts the Developer Agent's technical plan
    into actual source-code files.
    """

    def __init__(self, provider: str = "gemini"):
        self.provider = provider
        self.llm = get_llm(provider)

    def run(self, technical_plan: str) -> str:
        """
        Generate source-code files based on the
        Developer Agent's technical plan.
        """

        prompt = f"""
You are the Code Generator Agent of a professional
multi-agent software development team.

The Developer Agent has created the following
technical implementation plan:

--------------------------------------------------
{technical_plan}
--------------------------------------------------

Your responsibility is to generate the actual
source-code files required to implement the project.

Follow these rules:

1. Generate complete and functional code.
2. Follow the technology stack specified in the plan.
3. Create only the files that are actually required.
4. Every file must have a clear relative file path.
5. Include all necessary imports.
6. Make sure the generated files work together.
7. Keep the code modular and maintainable.
8. Do not use TODO placeholders.
9. Do not provide incomplete code.
10. Do not write lengthy explanations.

Return every file using this format:

FILE: path/to/file.ext

<START OF FILE>
complete file content
<END OF FILE>

For example:

FILE: backend/main.py

<START OF FILE>
from fastapi import FastAPI

app = FastAPI()
<END OF FILE>

Generate all required project files.
"""

        # Send request to the LLM
        response = self.llm.invoke(prompt)

        # Extract response content
        content = response.content

        # Gemini may return content as a list
        if isinstance(content, list):

            text_parts = []

            for item in content:

                if isinstance(item, dict):
                    text = item.get("text")

                    if text:
                        text_parts.append(text)

                elif isinstance(item, str):
                    text_parts.append(item)

            return "\n".join(text_parts)

        # Normal string response
        return str(content)