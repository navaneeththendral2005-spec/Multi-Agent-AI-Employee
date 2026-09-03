import os

from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()


# =========================================================
# TAVILY CONFIGURATION
# =========================================================

TAVILY_API_KEY = os.getenv(
    "TAVILY_API_KEY"
)


# =========================================================
# WEB SEARCH
# =========================================================

def web_search(
    query: str,
    max_results: int = 5,
    search_depth: str = "basic",
) -> list[dict]:
    """
    Search the web using Tavily.

    Returns a normalized list of search results.
    """

    query = query.strip()

    if not query:
        return []

    if not TAVILY_API_KEY:
        raise RuntimeError(
            "TAVILY_API_KEY is not configured."
        )

    client = TavilyClient(
        api_key=TAVILY_API_KEY
    )

    response = client.search(
        query=query,
        search_depth=search_depth,
        max_results=max_results,
        include_answer=False,
        include_raw_content=False,
    )

    results = response.get(
        "results",
        []
    )

    normalized_results = []

    for result in results:

        if not isinstance(
            result,
            dict
        ):
            continue

        title = str(
            result.get(
                "title",
                ""
            )
        ).strip()

        url = str(
            result.get(
                "url",
                ""
            )
        ).strip()

        content = str(
            result.get(
                "content",
                ""
            )
        ).strip()

        if not title and not content:
            continue

        normalized_results.append(
            {
                "title": title,
                "url": url,
                "content": content,
            }
        )

    return normalized_results