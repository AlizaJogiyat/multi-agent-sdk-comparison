"""Research Agent — searches the web, gathers company data into a structured brief."""

import json
import logging

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from tools.web_search_server import create_web_search_server
from tools.calculator_server import create_calculator_server
from tools.file_writer_server import create_file_writer_server

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Research Agent for an investment analysis pipeline.

Your job is to gather comprehensive research data about a company and produce a structured JSON brief.

You have access to these tools:
- web_search: Search the web for company information
- calculate: Perform financial calculations
- write_file: Save files to disk

INSTRUCTIONS:
1. Search for the company's recent news, financial data, competitors, and filings
2. Compile your findings into a structured JSON brief
3. If you cannot find data for a section, mark it as "no data found" — do NOT hallucinate

Your final output MUST be a valid JSON object with exactly this structure:
{
  "company_overview": {
    "name": "...",
    "description": "...",
    "industry": "...",
    "founded": "...",
    "headquarters": "..."
  },
  "financials": {
    "revenue": "...",
    "net_income": "...",
    "growth_rate": "...",
    "margins": "...",
    "key_metrics": {}
  },
  "competitors": [
    {"name": "...", "description": "...", "market_position": "..."}
  ],
  "recent_news": [
    {"headline": "...", "summary": "...", "date": "..."}
  ]
}

Output ONLY the JSON object, no markdown fences, no commentary."""


async def run_research_agent(company_name: str) -> dict:
    """Run the Research Agent to gather data about a company.

    Args:
        company_name: Name of the company to research.

    Returns:
        Structured JSON brief with company_overview, financials, competitors, recent_news.
    """
    logger.info("Research Agent started for company: %s", company_name)

    web_search_server = create_web_search_server()
    calculator_server = create_calculator_server()
    file_writer_server = create_file_writer_server()

    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        max_turns=15,
        mcp_servers={
            "web_search": web_search_server,
            "calculator": calculator_server,
            "file_writer": file_writer_server,
        },
        allowed_tools=[
            "mcp__web_search__*",
            "mcp__calculator__*",
            "mcp__file_writer__*",
        ],
    )

    prompt = (
        f"Research the company '{company_name}'. "
        f"Search for recent news, financial data, competitors, and company overview. "
        f"Return a structured JSON brief."
    )

    result_text = ""
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            result_text = message.result

    if not result_text:
        logger.warning("Research Agent returned empty result for %s", company_name)
        return _empty_brief(company_name)

    try:
        # Try to extract JSON from the result
        brief = _extract_json(result_text)
        _validate_brief(brief, company_name)
        logger.info("Research Agent completed for %s", company_name)
        return brief
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("Failed to parse Research Agent output: %s", e)
        return _empty_brief(company_name)


def _extract_json(text: str) -> dict:
    """Extract JSON from text, handling markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)


def _validate_brief(brief: dict, company_name: str):
    """Ensure brief has required top-level keys."""
    required = ["company_overview", "financials", "competitors", "recent_news"]
    for key in required:
        if key not in brief:
            brief[key] = "no data found"


def _empty_brief(company_name: str) -> dict:
    return {
        "company_overview": {"name": company_name, "description": "no data found", "industry": "no data found", "founded": "no data found", "headquarters": "no data found"},
        "financials": {"revenue": "no data found", "net_income": "no data found", "growth_rate": "no data found", "margins": "no data found", "key_metrics": {}},
        "competitors": [],
        "recent_news": [],
    }
