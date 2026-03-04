"""Analysis Agent — performs financial analysis and risk scoring."""

import json
import logging

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from tools.web_search_server import create_web_search_server
from tools.calculator_server import create_calculator_server
from tools.file_writer_server import create_file_writer_server

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an Analysis Agent for an investment analysis pipeline.

You receive a research brief (JSON) about a company and must produce a financial analysis.

You have access to these tools:
- web_search: Search for additional financial data if needed
- calculate: Perform financial calculations (revenue_growth, profit_margin, debt_to_equity, current_ratio, roi, expression)
- write_file: Save files to disk

INSTRUCTIONS:
1. Review the research brief carefully
2. Use the calculator tool to compute financial metrics where data is available
3. Identify key risks (market, regulatory, operational)
4. Score the investment opportunity on a 1-10 scale with justification
5. If financial data is missing or marked "no data found", flag those fields as "insufficient data" and adjust your confidence accordingly

Your final output MUST be a valid JSON object with exactly this structure:
{
  "calculations": {
    "revenue_growth_pct": null or number,
    "profit_margin_pct": null or number,
    "debt_to_equity_ratio": null or number,
    "current_ratio": null or number,
    "additional_metrics": {}
  },
  "risks": [
    {"category": "market|regulatory|operational", "description": "...", "severity": "high|medium|low"}
  ],
  "opportunity_score": 1-10,
  "justification": "...",
  "confidence": "high|medium|low",
  "data_gaps": ["list of fields with insufficient data"]
}

Output ONLY the JSON object, no markdown fences, no commentary."""


async def run_analysis_agent(research_brief: dict) -> dict:
    """Run the Analysis Agent on a research brief.

    Args:
        research_brief: Structured research brief from the Research Agent.

    Returns:
        Structured analysis with calculations, risks, opportunity_score, justification.
    """
    logger.info("Analysis Agent started")

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

    brief_json = json.dumps(research_brief, indent=2)
    prompt = (
        f"Analyze the following research brief and produce a financial analysis:\n\n"
        f"{brief_json}"
    )

    result_text = ""
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            result_text = message.result

    if not result_text:
        logger.warning("Analysis Agent returned empty result")
        return _default_analysis()

    try:
        analysis = _extract_json(result_text)
        _validate_analysis(analysis)
        logger.info("Analysis Agent completed — opportunity_score: %s", analysis.get("opportunity_score"))
        return analysis
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("Failed to parse Analysis Agent output: %s", e)
        return _default_analysis()


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)


def _validate_analysis(analysis: dict):
    required = ["calculations", "risks", "opportunity_score", "justification"]
    for key in required:
        if key not in analysis:
            analysis[key] = "insufficient data" if key != "opportunity_score" else 5
    if "confidence" not in analysis:
        analysis["confidence"] = "low"
    if "data_gaps" not in analysis:
        analysis["data_gaps"] = []


def _default_analysis() -> dict:
    return {
        "calculations": {
            "revenue_growth_pct": None,
            "profit_margin_pct": None,
            "debt_to_equity_ratio": None,
            "current_ratio": None,
            "additional_metrics": {},
        },
        "risks": [{"category": "operational", "description": "Insufficient data for analysis", "severity": "high"}],
        "opportunity_score": 5,
        "justification": "Insufficient data to produce a confident analysis.",
        "confidence": "low",
        "data_gaps": ["All financial fields — analysis based on limited data"],
    }
