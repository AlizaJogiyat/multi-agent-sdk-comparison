"""
Claude Agent Pipeline Runner — async SSE streaming wrapper.
Imports all agent logic from claude-agent/agent_system.py (single source of truth).
"""

import asyncio
import json
import sys
from pathlib import Path

# Add claude-agent to sys.path so we can import agent_system
_claude_agent_dir = str(Path(__file__).parent.parent.parent / "claude-agent")
if _claude_agent_dir not in sys.path:
    sys.path.insert(0, _claude_agent_dir)

from agent_system import (
    get_client,
    process_tool_call,
    MODEL,
    RESEARCHER_TOOLS,
    ANALYZER_TOOLS,
    WRITER_TOOLS,
    QA_TOOLS,
)

# Initialize client with explicit .env path
_env_path = str(Path(__file__).parent.parent.parent / "claude-agent" / ".env")
client = get_client(env_path=_env_path)


# ============================================================================
# REAL-TIME STREAMING AGENT RUNNER
# ============================================================================


def _run_single_iteration(tools: list, messages: list, max_tokens: int):
    """Run one blocking Anthropic API call."""
    return client.messages.create(
        model=MODEL, max_tokens=max_tokens, tools=tools, messages=messages
    )


async def _run_agent_streaming(
    agent_name: str,
    tools: list,
    messages: list,
    queue: asyncio.Queue,
    max_tokens: int = 1024,
):
    """Run an agent loop, pushing events to queue in real-time."""
    iteration = 1
    final_output = None

    while True:
        await queue.put({"type": "iteration", "message": f"[{agent_name}] Iteration {iteration}"})

        response = await asyncio.to_thread(_run_single_iteration, tools, messages, max_tokens)

        await queue.put({"type": "iteration", "message": f"[{agent_name}] Stop reason: {response.stop_reason}"})

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    await queue.put({
                        "type": "tool_call",
                        "message": f"[{agent_name}] Calling tool: {block.name}({json.dumps(block.input)[:150]})",
                    })
                    tool_result = process_tool_call(block.name, block.input)
                    await queue.put({
                        "type": "tool_result",
                        "message": f"[{agent_name}] Tool result received ({len(tool_result)} chars)",
                    })
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_result,
                    })
                elif block.type == "text" and block.text:
                    await queue.put({
                        "type": "agent_text",
                        "message": f"[{agent_name}] {block.text[:300]}",
                    })

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    final_output = block.text
            await queue.put({"type": "agent_complete", "message": f"[{agent_name}] Completed"})
            break

        elif response.stop_reason == "max_tokens":
            for block in response.content:
                if block.type == "text" and block.text:
                    await queue.put({
                        "type": "agent_text",
                        "message": f"[{agent_name}] {block.text[:300]}...",
                    })
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": "Please continue."})

        iteration += 1

    return final_output


async def _drain_queue(queue: asyncio.Queue, task: asyncio.Task):
    """Drain events from queue while task is running, yielding each one."""
    while not task.done():
        try:
            event = await asyncio.wait_for(queue.get(), timeout=0.5)
            yield event
        except asyncio.TimeoutError:
            continue
    # Drain remaining
    while not queue.empty():
        yield await queue.get()


async def run_pipeline(company_name: str):
    """Async generator yielding SSE events for the full 4-agent pipeline."""

    queue: asyncio.Queue = asyncio.Queue()

    yield {"type": "pipeline_start", "message": f"Starting pipeline for: {company_name}"}

    # ── Agent 1: Researcher ──
    yield {"type": "agent_start", "message": "========== Agent 1: RESEARCHER =========="}

    researcher_messages = [
        {
            "role": "user",
            "content": f"Search for information about {company_name} including their founding year, revenue, number of employees, and sector. Provide a brief research summary.",
        }
    ]

    task = asyncio.create_task(
        _run_agent_streaming("Researcher", RESEARCHER_TOOLS, researcher_messages, queue)
    )
    async for event in _drain_queue(queue, task):
        yield event
    research_output = await task

    if not research_output:
        yield {"type": "error", "message": "Researcher agent produced no output"}
        return
    yield {"type": "agent_output", "message": f"[Researcher Output]\n{research_output}"}

    # ── Agent 2: Analyzer ──
    yield {"type": "agent_start", "message": "========== Agent 2: ANALYZER =========="}

    analyzer_messages = [
        {
            "role": "user",
            "content": f"""You have received the following research brief from the Research Agent:

{research_output}

Please analyze this information by:
1. Calculating the revenue_per_employee metric
2. Scoring the investment opportunity
3. Providing your investment recommendation

Use the available tools to complete this analysis.""",
        }
    ]

    task = asyncio.create_task(
        _run_agent_streaming("Analyzer", ANALYZER_TOOLS, analyzer_messages, queue)
    )
    async for event in _drain_queue(queue, task):
        yield event
    analysis_output = await task

    if not analysis_output:
        yield {"type": "error", "message": "Analyzer agent produced no output"}
        return
    yield {"type": "agent_output", "message": f"[Analyzer Output]\n{analysis_output}"}

    # ── Agent 3: Writer ──
    yield {"type": "agent_start", "message": "========== Agent 3: WRITER =========="}

    writer_messages = [
        {
            "role": "user",
            "content": f"""You are an investment memo writer. You have received the following inputs:

--- RESEARCH BRIEF (from Researcher Agent) ---
{research_output}

--- ANALYSIS BRIEF (from Analyzer Agent) ---
{analysis_output}

Draft a professional 2-page investment memo for {company_name}. Use the format_memo tool with these sections:
1. Executive Summary - 2-3 sentence overview
2. Company Overview - What the company does, founding, sector
3. Financial Analysis - Key metrics and growth potential
4. Investment Thesis - Why this is compelling
5. Key Risks - 3-4 bullet points
6. Recommendation - Final investment recommendation

Keep it professional and concise.""",
        }
    ]

    task = asyncio.create_task(
        _run_agent_streaming("Writer", WRITER_TOOLS, writer_messages, queue, max_tokens=4096)
    )
    async for event in _drain_queue(queue, task):
        yield event
    writer_output = await task

    if writer_output:
        yield {"type": "agent_output", "message": f"[Writer Output]\n{writer_output}"}

    # ── Agent 4: QA/Review ──
    yield {"type": "agent_start", "message": "========== Agent 4: QA / REVIEW =========="}

    qa_messages = [
        {
            "role": "user",
            "content": f"""You are a senior QA reviewer for investment memos. Your job is to ensure factual accuracy and flag any problems.

You have 3 documents to cross-reference:

--- ORIGINAL RESEARCH (Source of Truth) ---
{research_output}

--- ANALYSIS ---
{analysis_output}

--- INVESTMENT MEMO (To Review) ---
{writer_output}

Your task:
1. **Fact-check** at least 3-5 key claims in the memo against the original research data using the fact_check tool.
2. **Flag issues** using the flag_issue tool for any hallucinations, inconsistencies, unsupported claims, or missing information.
3. Provide a final QA summary with:
   - Overall quality score (1-10)
   - Number of issues found by severity
   - Whether the memo is APPROVED, NEEDS REVISION, or REJECTED
   - Specific revision requests if needed""",
        }
    ]

    task = asyncio.create_task(
        _run_agent_streaming("QA", QA_TOOLS, qa_messages, queue, max_tokens=4096)
    )
    async for event in _drain_queue(queue, task):
        yield event
    qa_output = await task

    if qa_output:
        yield {"type": "agent_output", "message": f"[QA Output]\n{qa_output}"}

    # ── Final summary ──
    yield {
        "type": "pipeline_complete",
        "message": "Pipeline complete! All 4 agents finished successfully.",
        "research": research_output or "",
        "analysis": analysis_output or "",
        "memo": writer_output or "",
        "qa_review": qa_output or "",
    }
