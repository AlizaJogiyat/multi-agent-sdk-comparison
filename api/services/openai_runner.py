"""
OpenAI Agent Pipeline Runner — async SSE streaming wrapper.
Imports all agent logic from openai-agent/agent_system.py (single source of truth).
"""

import asyncio
import json
import importlib.util
from pathlib import Path

# Import openai-agent/agent_system.py by absolute file path to avoid
# collision with claude-agent/agent_system.py on sys.path.
_openai_agent_file = Path(__file__).parent.parent.parent / "openai-agent" / "agent_system.py"
_spec = importlib.util.spec_from_file_location("openai_agent_system", str(_openai_agent_file))
_oai_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_oai_mod)

researcher_agent = _oai_mod.researcher_agent
analyzer_agent = _oai_mod.analyzer_agent
writer_agent = _oai_mod.writer_agent
qa_agent = _oai_mod.qa_agent

from agents import Runner

# Load env with explicit path
_env_path = str(Path(__file__).parent.parent.parent / "openai-agent" / ".env")
_oai_mod.load_env(env_path=_env_path)


async def _run_agent_streaming(
    agent_name: str,
    agent,
    input_text: str,
    queue: asyncio.Queue,
):
    """Run an OpenAI agent, pushing events to queue in real-time."""
    await queue.put({"type": "iteration", "message": f"[{agent_name}] Starting agent run..."})

    try:
        result = await Runner.run(agent, input=input_text)
        final_output = result.final_output

        # Emit info about new_items (tool calls, messages, etc.)
        if hasattr(result, 'new_items'):
            for item in result.new_items:
                item_type = type(item).__name__
                if 'ToolCall' in item_type:
                    tool_name = getattr(item, 'name', None) or getattr(item, 'tool_name', 'unknown')
                    tool_args = getattr(item, 'arguments', None) or getattr(item, 'input', '')
                    await queue.put({
                        "type": "tool_call",
                        "message": f"[{agent_name}] Calling tool: {tool_name}({str(tool_args)[:150]})",
                    })
                elif 'ToolOutput' in item_type or 'ToolResult' in item_type:
                    output_text = getattr(item, 'output', '') or getattr(item, 'result', '')
                    await queue.put({
                        "type": "tool_result",
                        "message": f"[{agent_name}] Tool result received ({len(str(output_text))} chars)",
                    })
                elif 'Message' in item_type:
                    content = getattr(item, 'content', '')
                    if content and isinstance(content, str) and len(content) > 0:
                        await queue.put({
                            "type": "agent_text",
                            "message": f"[{agent_name}] {str(content)[:300]}",
                        })

        await queue.put({"type": "agent_complete", "message": f"[{agent_name}] Completed"})
        return final_output

    except Exception as e:
        await queue.put({"type": "error", "message": f"[{agent_name}] Error: {str(e)}"})
        return None


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

    yield {"type": "pipeline_start", "message": f"Starting OpenAI pipeline for: {company_name}"}

    # ── Agent 1: Researcher ──
    yield {"type": "agent_start", "message": "========== Agent 1: RESEARCHER =========="}

    researcher_input = f"Search for information about {company_name} including their founding year, revenue, number of employees, and sector. Provide a brief research summary."

    task = asyncio.create_task(
        _run_agent_streaming("Researcher", researcher_agent, researcher_input, queue)
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

    analyzer_input = f"""You have received the following research brief from the Research Agent:

{research_output}

Please analyze this information by:
1. Calculating the revenue_per_employee metric
2. Scoring the investment opportunity
3. Providing your investment recommendation

Use the available tools to complete this analysis."""

    task = asyncio.create_task(
        _run_agent_streaming("Analyzer", analyzer_agent, analyzer_input, queue)
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

    writer_input = f"""You are an investment memo writer. You have received the following inputs:

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

Keep it professional and concise."""

    task = asyncio.create_task(
        _run_agent_streaming("Writer", writer_agent, writer_input, queue)
    )
    async for event in _drain_queue(queue, task):
        yield event
    writer_output = await task

    if writer_output:
        yield {"type": "agent_output", "message": f"[Writer Output]\n{writer_output}"}

    # ── Agent 4: QA/Review ──
    yield {"type": "agent_start", "message": "========== Agent 4: QA / REVIEW =========="}

    qa_input = f"""You are a senior QA reviewer for investment memos. Your job is to ensure factual accuracy and flag any problems.

You have 3 documents to cross-reference:

--- ORIGINAL RESEARCH (Source of Truth) ---
{research_output}

--- ANALYSIS ---
{analysis_output}

--- INVESTMENT MEMO (To Review) ---
{writer_output}

Your task:
1. Fact-check at least 3-5 key claims in the memo against the original research data using the fact_check tool.
2. Flag issues using the flag_issue tool for any hallucinations, inconsistencies, unsupported claims, or missing information.
3. Provide a final QA summary with:
   - Overall quality score (1-10)
   - Number of issues found by severity
   - Whether the memo is APPROVED, NEEDS REVISION, or REJECTED
   - Specific revision requests if needed"""

    task = asyncio.create_task(
        _run_agent_streaming("QA", qa_agent, qa_input, queue)
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