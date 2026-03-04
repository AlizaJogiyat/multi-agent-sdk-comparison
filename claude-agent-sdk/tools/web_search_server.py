"""MCP tool server for web search functionality."""

from claude_agent_sdk import tool, create_sdk_mcp_server

import json
import urllib.request
import urllib.parse
import urllib.error


@tool(
    "web_search",
    "Search the web for information about a topic. Returns search results as JSON.",
    {"query": str},
)
async def web_search(args):
    """Perform a web search using DuckDuckGo Instant Answer API."""
    query = args["query"]
    try:
        encoded = urllib.parse.urlencode({"q": query, "format": "json", "no_html": "1"})
        url = f"https://api.duckduckgo.com/?{encoded}"
        req = urllib.request.Request(url, headers={"User-Agent": "InvestmentMemoPipeline/1.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())

        results = []

        if data.get("Abstract"):
            results.append({
                "title": data.get("Heading", ""),
                "snippet": data["Abstract"],
                "source": data.get("AbstractSource", ""),
                "url": data.get("AbstractURL", ""),
            })

        for topic in data.get("RelatedTopics", [])[:5]:
            if isinstance(topic, dict) and "Text" in topic:
                results.append({
                    "title": topic.get("Text", "")[:100],
                    "snippet": topic.get("Text", ""),
                    "url": topic.get("FirstURL", ""),
                })

        if not results:
            results = [{"title": "no data found", "snippet": "No search results available for this query."}]

        return {"content": [{"type": "text", "text": json.dumps(results, indent=2)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": json.dumps({"error": str(e), "query": query})}]}


def create_web_search_server():
    return create_sdk_mcp_server(
        name="web_search",
        version="1.0.0",
        tools=[web_search],
    )
