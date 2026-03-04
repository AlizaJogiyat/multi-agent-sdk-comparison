"""QA/Review Agent — checks memo for factual consistency, flags hallucinations."""

import json
import logging

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from tools.web_search_server import create_web_search_server
from tools.calculator_server import create_calculator_server
from tools.file_writer_server import create_file_writer_server

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a QA/Review Agent for an investment analysis pipeline.

You receive:
1. The original research brief (JSON)
2. The investment memo (markdown)

Your job is to cross-reference every factual claim in the memo against the research brief and flag any hallucinations.

You have access to these tools:
- web_search: Verify facts by searching the web
- calculate: Re-verify calculations
- write_file: Save the QA report to disk

INSTRUCTIONS:
1. Read the memo carefully
2. For each factual claim (numbers, dates, company details), check if it exists in the research brief
3. Flag any data points in the memo that are NOT present in the research brief as potential hallucinations
4. Include a suggested correction or removal for each flagged item

Your final output MUST be a valid JSON object with exactly this structure:
{
  "verified_claims": [
    {"claim": "...", "source_in_brief": "..."}
  ],
  "unverified_claims": [
    {"claim": "...", "reason": "not found in brief"}
  ],
  "flagged_hallucinations": [
    {"memo_excerpt": "...", "expected_source": "...", "suggestion": "remove or correct to ..."}
  ],
  "revision_required": true/false,
  "revision_instructions": "..." or null,
  "factual_consistency_score": 0.0-1.0
}

Output ONLY the JSON object, no markdown fences, no commentary."""


async def run_qa_agent(research_brief: dict, memo: str) -> dict:
    """Run the QA/Review Agent to check a memo for factual consistency.

    Args:
        research_brief: Original research brief from the Research Agent.
        memo: The investment memo from the Writer Agent.

    Returns:
        Consistency report with verified/unverified claims and hallucinations.
    """
    logger.info("QA/Review Agent started")

    web_search_server = create_web_search_server()
    calculator_server = create_calculator_server()
    file_writer_server = create_file_writer_server()

    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        max_turns=10,
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
        f"Review this investment memo for factual consistency against the research brief.\n\n"
        f"=== RESEARCH BRIEF ===\n{brief_json}\n\n"
        f"=== INVESTMENT MEMO ===\n{memo}"
    )

    result_text = ""
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            result_text = message.result

    if not result_text:
        logger.warning("QA Agent returned empty result")
        return _default_report()

    try:
        report = _extract_json(result_text)
        _validate_report(report)
        logger.info(
            "QA Agent completed — revision_required: %s, consistency_score: %s",
            report.get("revision_required"),
            report.get("factual_consistency_score"),
        )
        return report
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("Failed to parse QA Agent output: %s", e)
        return _default_report()


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)


def _validate_report(report: dict):
    defaults = {
        "verified_claims": [],
        "unverified_claims": [],
        "flagged_hallucinations": [],
        "revision_required": False,
        "revision_instructions": None,
        "factual_consistency_score": 0.0,
    }
    for key, default in defaults.items():
        if key not in report:
            report[key] = default

    # Determine revision_required from hallucinations if not explicitly set
    if report["flagged_hallucinations"]:
        report["revision_required"] = True


def _default_report() -> dict:
    return {
        "verified_claims": [],
        "unverified_claims": [],
        "flagged_hallucinations": [],
        "revision_required": False,
        "revision_instructions": None,
        "factual_consistency_score": 0.0,
    }
