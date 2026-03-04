"""Writer Agent — drafts a 2-page investment memo in markdown."""

import json
import logging

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

from tools.web_search_server import create_web_search_server
from tools.calculator_server import create_calculator_server
from tools.file_writer_server import create_file_writer_server

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Writer Agent for an investment analysis pipeline.

You receive an analysis output (JSON) and must draft a 2-page investment memo in markdown format.

You have access to these tools:
- web_search: Search for additional context if needed
- calculate: Perform calculations if needed
- write_file: Save the memo to disk

INSTRUCTIONS:
1. Draft a professional investment memo in markdown
2. The memo MUST contain exactly these 5 sections with these exact headings:
   - ## Executive Summary
   - ## Company Overview
   - ## Financial Analysis
   - ## Risk Assessment
   - ## Recommendation
3. Reference specific data points from the analysis (numbers, percentages, scores)
4. Target length: 800-1200 words (approximately 2 pages)
5. Use the write_file tool to save the memo to 'output/memo.md'

Output the complete memo in markdown format."""


async def run_writer_agent(analysis_output: dict, revision_instructions: str | None = None) -> str:
    """Run the Writer Agent to draft an investment memo.

    Args:
        analysis_output: Structured analysis from the Analysis Agent.
        revision_instructions: Optional revision instructions from QA Agent.

    Returns:
        The investment memo as a markdown string.
    """
    logger.info("Writer Agent started%s", " (revision)" if revision_instructions else "")

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

    analysis_json = json.dumps(analysis_output, indent=2)

    if revision_instructions:
        prompt = (
            f"Revise the investment memo based on these QA feedback instructions:\n\n"
            f"{revision_instructions}\n\n"
            f"Original analysis data:\n{analysis_json}\n\n"
            f"Write the complete revised memo."
        )
    else:
        prompt = (
            f"Draft a 2-page investment memo based on this analysis:\n\n"
            f"{analysis_json}"
        )

    result_text = ""
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            result_text = message.result

    if not result_text:
        logger.warning("Writer Agent returned empty result")
        return ""

    logger.info("Writer Agent completed — %d characters", len(result_text))
    return result_text
