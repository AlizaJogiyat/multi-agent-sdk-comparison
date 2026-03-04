"""Orchestrator pipeline — sequential agent execution with validation and revision loops."""

import json
import logging
import time
import traceback
from dataclasses import dataclass, field

from config import (
    validate_config,
    MAX_REVISION_CYCLES,
    MAX_WRITER_VALIDATION_RETRIES,
    MEMO_MIN_WORDS,
    MEMO_MAX_WORDS,
    MEMO_REQUIRED_SECTIONS,
)
from agents.research_agent import run_research_agent
from agents.analysis_agent import run_analysis_agent
from agents.writer_agent import run_writer_agent
from agents.qa_agent import run_qa_agent

logger = logging.getLogger(__name__)


@dataclass
class AgentMetrics:
    """Token and timing metrics for a single agent run."""
    agent_name: str
    start_time: float = 0.0
    end_time: float = 0.0
    tokens_used: int = 0
    tool_calls: int = 0
    success: bool = False
    error: str | None = None


@dataclass
class PipelineState:
    """Shared state object accumulating all intermediate agent outputs."""
    company_name: str
    research_brief: dict | None = None
    analysis_output: dict | None = None
    memo: str | None = None
    qa_report: dict | None = None
    metrics: list[AgentMetrics] = field(default_factory=list)
    handoff_success: bool = True


class PipelineError(Exception):
    """Raised when the pipeline must abort."""
    def __init__(self, agent_name: str, stage: str, message: str):
        self.agent_name = agent_name
        self.stage = stage
        super().__init__(f"[{agent_name}] {stage}: {message}")


def validate_analysis_input(analysis_output: dict) -> list[str]:
    """Check analysis output has required fields for the Writer Agent."""
    required = ["calculations", "risks", "opportunity_score"]
    missing = [f for f in required if f not in analysis_output]
    return missing


def validate_memo_output(memo: str) -> list[str]:
    """Validate memo has required sections and word count."""
    issues = []
    for section in MEMO_REQUIRED_SECTIONS:
        if section.lower() not in memo.lower():
            issues.append(f"Missing section: {section}")
    word_count = len(memo.split())
    if word_count < MEMO_MIN_WORDS:
        issues.append(f"Too short: {word_count} words (min {MEMO_MIN_WORDS})")
    elif word_count > MEMO_MAX_WORDS:
        issues.append(f"Too long: {word_count} words (max {MEMO_MAX_WORDS})")
    return issues


async def run_pipeline(company_name: str) -> PipelineState:
    """Run the full 4-agent investment memo pipeline.

    Sequence: Research → Analysis → Writer → QA
    With validation gates and revision loops.

    Args:
        company_name: The company to analyze.

    Returns:
        PipelineState with all intermediate outputs and metrics.

    Raises:
        PipelineError: If a critical failure occurs.
    """
    validate_config()
    state = PipelineState(company_name=company_name)

    # === Stage 1: Research Agent ===
    metrics = AgentMetrics(agent_name="Research Agent")
    metrics.start_time = time.time()
    try:
        logger.info("=== Stage 1: Research Agent ===")
        state.research_brief = await run_research_agent(company_name)
        metrics.success = True
    except Exception as e:
        metrics.error = str(e)
        logger.error("Research Agent failed: %s\n%s", e, traceback.format_exc())
        raise PipelineError("Research Agent", "data_gathering", str(e)) from e
    finally:
        metrics.end_time = time.time()
        state.metrics.append(metrics)

    # === Stage 2: Analysis Agent ===
    metrics = AgentMetrics(agent_name="Analysis Agent")
    metrics.start_time = time.time()
    try:
        logger.info("=== Stage 2: Analysis Agent ===")
        state.analysis_output = await run_analysis_agent(state.research_brief)
        metrics.success = True
    except Exception as e:
        metrics.error = str(e)
        logger.error("Analysis Agent failed: %s\n%s", e, traceback.format_exc())
        raise PipelineError("Analysis Agent", "financial_analysis", str(e)) from e
    finally:
        metrics.end_time = time.time()
        state.metrics.append(metrics)

    # === Input Validation Gate for Writer ===
    missing = validate_analysis_input(state.analysis_output)
    if missing:
        error_msg = f"Analysis output missing required fields: {', '.join(missing)}"
        logger.error(error_msg)
        raise PipelineError("Writer Agent", "input_validation", error_msg)

    # === Stage 3: Writer Agent (with output validation retries) ===
    memo = ""
    for attempt in range(1, MAX_WRITER_VALIDATION_RETRIES + 1):
        metrics = AgentMetrics(agent_name=f"Writer Agent (attempt {attempt})")
        metrics.start_time = time.time()
        try:
            logger.info("=== Stage 3: Writer Agent (attempt %d/%d) ===", attempt, MAX_WRITER_VALIDATION_RETRIES)
            revision_note = None
            if attempt > 1:
                issues_str = "; ".join(validate_memo_output(memo))
                revision_note = f"Previous memo had validation issues: {issues_str}. Fix them."
            memo = await run_writer_agent(state.analysis_output, revision_instructions=revision_note)
            metrics.success = True
        except Exception as e:
            metrics.error = str(e)
            logger.error("Writer Agent failed: %s\n%s", e, traceback.format_exc())
            raise PipelineError("Writer Agent", "memo_drafting", str(e)) from e
        finally:
            metrics.end_time = time.time()
            state.metrics.append(metrics)

        # Output validation
        issues = validate_memo_output(memo)
        if not issues:
            break
        logger.warning("Writer output validation failed (attempt %d): %s", attempt, issues)
    else:
        logger.warning("Writer Agent failed validation after %d attempts — proceeding with best-effort memo", MAX_WRITER_VALIDATION_RETRIES)

    state.memo = memo

    # === Stage 4: QA/Review Agent (with revision loop) ===
    for cycle in range(1, MAX_REVISION_CYCLES + 1):
        metrics = AgentMetrics(agent_name=f"QA Agent (cycle {cycle})")
        metrics.start_time = time.time()
        try:
            logger.info("=== Stage 4: QA Agent (cycle %d/%d) ===", cycle, MAX_REVISION_CYCLES)
            qa_report = await run_qa_agent(state.research_brief, state.memo)
            metrics.success = True
        except Exception as e:
            metrics.error = str(e)
            logger.error("QA Agent failed: %s\n%s", e, traceback.format_exc())
            raise PipelineError("QA Agent", "consistency_check", str(e)) from e
        finally:
            metrics.end_time = time.time()
            state.metrics.append(metrics)

        state.qa_report = qa_report

        if not qa_report.get("revision_required", False):
            logger.info("QA Agent: memo passed — no revisions needed")
            break

        logger.info("QA Agent: revision required (cycle %d/%d)", cycle, MAX_REVISION_CYCLES)

        if cycle < MAX_REVISION_CYCLES:
            # Re-invoke Writer with revision instructions
            revision_instructions = qa_report.get("revision_instructions", "Fix flagged hallucinations.")
            metrics = AgentMetrics(agent_name=f"Writer Agent (revision {cycle})")
            metrics.start_time = time.time()
            try:
                state.memo = await run_writer_agent(
                    state.analysis_output,
                    revision_instructions=revision_instructions,
                )
                metrics.success = True
            except Exception as e:
                metrics.error = str(e)
                logger.error("Writer revision failed: %s\n%s", e, traceback.format_exc())
                raise PipelineError("Writer Agent", f"revision_{cycle}", str(e)) from e
            finally:
                metrics.end_time = time.time()
                state.metrics.append(metrics)
    else:
        logger.warning(
            "QA revision loop exhausted after %d cycles — proceeding with best-effort memo",
            MAX_REVISION_CYCLES,
        )

    _log_pipeline_summary(state)
    return state


def _log_pipeline_summary(state: PipelineState):
    """Log a structured summary of the pipeline run."""
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE: %s", state.company_name)
    logger.info("=" * 60)
    total_time = 0.0
    for m in state.metrics:
        duration = m.end_time - m.start_time
        total_time += duration
        status = "OK" if m.success else f"FAILED: {m.error}"
        logger.info("  %-30s  %6.1fs  %s", m.agent_name, duration, status)
    logger.info("  %-30s  %6.1fs", "TOTAL", total_time)
    if state.qa_report:
        score = state.qa_report.get("factual_consistency_score", "N/A")
        logger.info("  Factual consistency score: %s", score)
    logger.info("=" * 60)


if __name__ == "__main__":
    import asyncio
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    company = sys.argv[1] if len(sys.argv) > 1 else "Stripe"

    async def main():
        try:
            state = await run_pipeline(company)
            if state.memo:
                print("\n=== FINAL MEMO ===\n")
                print(state.memo)
        except PipelineError as e:
            logger.error("Pipeline aborted: %s", e)
            sys.exit(1)

    asyncio.run(main())
