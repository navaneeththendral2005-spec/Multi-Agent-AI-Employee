from agents.base_agent import BaseAgent
from research_tools.web_search import web_search


class ResearchAgent(BaseAgent):
    """
    Research Agent for CHORUS.

    Responsibilities:
    - Information gathering
    - Live web research
    - Fact finding
    - Comparison
    - Organizing research
    - Identifying uncertainty
    - Providing source references
    """

    def __init__(
        self,
        provider: str = "gemini"
    ):
        super().__init__(
            "research",
            provider
        )

    # =========================================================
    # RESEARCH
    # =========================================================

    def run(
        self,
        task: str
    ) -> str:
        """
        Execute the assigned research task.

        Tavily performs web retrieval.
        The configured LLM analyzes and synthesizes
        the retrieved information.
        """

        task = task.strip()

        if not task:

            return (
                "RESEARCH FAILED\n\n"
                "No research task was provided."
            )

        # =====================================================
        # WEB SEARCH
        # =====================================================

        try:

            search_results = web_search(
                query=task,
                max_results=5,
                search_depth="basic",
            )

        except Exception as error:

            return (
                "RESEARCH FAILED\n\n"
                "Web search could not be completed.\n"
                f"Error: {error}"
            )

        # =====================================================
        # CHECK SEARCH RESULTS
        # =====================================================

        if not search_results:

            return (
                "RESEARCH FAILED\n\n"
                "No relevant web search results "
                "were found for this request."
            )

        # =====================================================
        # PREPARE SOURCES FOR LLM
        # =====================================================

        source_blocks = []

        for index, result in enumerate(
            search_results,
            start=1
        ):

            title = result.get(
                "title",
                "Untitled source"
            )

            url = result.get(
                "url",
                ""
            )

            content = result.get(
                "content",
                ""
            )

            source_blocks.append(
                f"""
SOURCE {index}

Title:
{title}

URL:
{url}

Content:
{content}
""".strip()
            )

        sources_text = "\n\n".join(
            source_blocks
        )

        # =====================================================
        # LLM RESEARCH SYNTHESIS
        # =====================================================

        prompt = f"""
You are CHORUS's Research Agent.

You have access to real web-search results retrieved
through Tavily.

Complete ONLY the research task below.

ASSIGNED TASK:
{task}

WEB SEARCH RESULTS:
{sources_text}

RULES:

1. Base factual claims primarily on the supplied
   web-search results.

2. Do not invent facts, statistics, quotes, sources,
   or URLs.

3. Do not claim something is confirmed if the supplied
   sources do not support it.

4. Clearly distinguish confirmed information from
   uncertainty or conflicting information.

5. Prefer recent information when the task requires
   current information.

6. Use multiple sources when appropriate.

7. Do not blindly repeat information from one source.

8. If sources disagree, clearly mention the disagreement.

9. Keep the response focused on the assigned task.

10. Do not perform unrelated coding, document creation,
    data analysis, or communication tasks.

11. Do not mention Tavily unless it is relevant to
    explaining the research method.

12. Keep the answer concise unless the task explicitly
    requests a detailed report.

13. Include the actual source title and URL in the
    Sources / References section.

14. Never create a URL yourself. Only use URLs supplied
    by the web-search results.

RETURN:

RESEARCH SUMMARY
<concise synthesized answer>

KEY FINDINGS
• <finding>
• <finding>
• <finding>

FACTS / UNCERTAINTY
• Confirmed: <supported fact>
• Confirmed: <supported fact>
• Uncertain: <uncertainty, disagreement, or limitation>

SOURCES / REFERENCES
• <source title> — <URL>
• <source title> — <URL>
• <source title> — <URL>

LIMITATIONS
<short limitation statement>

Do not write an article unless the assigned task
explicitly requests one.
"""

        # =====================================================
        # INVOKE LLM
        # =====================================================

        try:

            response = self.invoke(
                prompt
            )

        except Exception as error:

            return (
                "RESEARCH FAILED\n\n"
                f"LLM error: {error}"
            )

        # =====================================================
        # NORMALIZE RESPONSE
        # =====================================================

        content = response.content

        if isinstance(content, list):

            text_parts = []

            for item in content:

                if isinstance(item, dict):

                    text = item.get(
                        "text"
                    )

                    if text:

                        text_parts.append(
                            str(text)
                        )

                elif isinstance(item, str):

                    text_parts.append(
                        item
                    )

            content = "\n".join(
                text_parts
            )

        else:

            content = str(
                content
            )

        content = content.strip()

        # =====================================================
        # EMPTY RESPONSE SAFETY
        # =====================================================

        if not content:

            return (
                "RESEARCH FAILED\n\n"
                "The Research Agent did not "
                "return a response."
            )

        return content