import os

from dotenv import load_dotenv
from tavily import TavilyClient

from src.tool_registry import tool

load_dotenv()


@tool(description="Search the internet for information")
def internet_search(
    query: str,
    max_results: int = 5,
    include_raw_content: bool = False,
):
    """Run a web search"""
    tavily_async_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    search_docs = tavily_async_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
    )
    return search_docs
