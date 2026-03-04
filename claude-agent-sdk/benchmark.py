"""Benchmark harness — runs the pipeline 20 times and generates reports."""

import asyncio
import json
import logging
import os
import time
from dataclasses import asdict

from config import validate_config, DEFAULT_COMPANY
from pipeline import run_pipeline, PipelineError, PipelineState

logger = logging.getLogger(__name__)

NUM_RUNS = 20

# Approximate Anthropic pricing (per 1M tokens) — adjust as needed
PRICING = {
    "input": 3.00,   # $3 per 1M input tokens (Sonnet)
    "output": 15.00,  # $15 per 1M output tokens (Sonnet)
}


def calculate_cost(total_tokens: int) -> float:
    """Estimate cost from total tokens (rough split: 70% input, 30% output)."""
    input_tokens = total_tokens * 0.7
    output_tokens = total_tokens * 0.3
    cost = (input_tokens / 1_000_000 * PRICING["input"]) + (output_tokens / 1_000_000 * PRICING["output"])
    return round(cost, 6)


async def run_benchmark(company_name: str = DEFAULT_COMPANY, num_runs: int = NUM_RUNS) -> dict:
    """Run the pipeline multiple times and collect metrics.

    Args:
        company_name: Canonical test input company.
        num_runs: Number of benchmark runs.

    Returns:
        Benchmark results dictionary.
    """
    validate_config()
    logger.info("Starting benchmark: %d runs for '%s'", num_runs, company_name)

    results = []

    for run_id in range(1, num_runs + 1):
        run_result = {
            "run_id": run_id,
            "company": company_name,
            "handoff_success": False,
            "total_time_s": 0.0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "agent_metrics": [],
            "error": None,
            "factual_consistency_score": None,
        }

        start = time.time()
        try:
            logger.info("=== Benchmark run %d/%d ===", run_id, num_runs)
            state = await run_pipeline(company_name)

            run_result["handoff_success"] = state.handoff_success
            run_result["agent_metrics"] = [
                {
                    "agent_name": m.agent_name,
                    "duration_s": round(m.end_time - m.start_time, 2),
                    "tokens_used": m.tokens_used,
                    "tool_calls": m.tool_calls,
                    "success": m.success,
                    "error": m.error,
                }
                for m in state.metrics
            ]

            total_tokens = sum(m.tokens_used for m in state.metrics)
            run_result["total_tokens"] = total_tokens
            run_result["cost_usd"] = calculate_cost(total_tokens)

            if state.qa_report:
                run_result["factual_consistency_score"] = state.qa_report.get("factual_consistency_score")

        except PipelineError as e:
            run_result["handoff_success"] = False
            run_result["error"] = str(e)
            logger.error("Run %d failed: %s", run_id, e)
        except Exception as e:
            run_result["handoff_success"] = False
            run_result["error"] = str(e)
            logger.error("Run %d unexpected error: %s", run_id, e)
        finally:
            run_result["total_time_s"] = round(time.time() - start, 2)

        results.append(run_result)

    report = _generate_report(results, company_name)
    _save_reports(report)
    return report


def _generate_report(results: list[dict], company_name: str) -> dict:
    """Generate aggregate benchmark report."""
    successful = [r for r in results if r["handoff_success"]]
    failed = [r for r in results if not r["handoff_success"]]

    total_runs = len(results)
    success_count = len(successful)
    handoff_success_rate = round(success_count / total_runs * 100, 1) if total_runs > 0 else 0

    avg_tokens = round(sum(r["total_tokens"] for r in successful) / len(successful)) if successful else 0
    avg_cost = round(sum(r["cost_usd"] for r in successful) / len(successful), 6) if successful else 0
    avg_time = round(sum(r["total_time_s"] for r in successful) / len(successful), 2) if successful else 0

    # Per-agent token breakdown
    agent_tokens: dict[str, list[int]] = {}
    for r in successful:
        for m in r["agent_metrics"]:
            name = m["agent_name"].split(" (")[0]  # Strip attempt/cycle suffix
            agent_tokens.setdefault(name, []).append(m["tokens_used"])

    tokens_per_agent = {
        name: round(sum(vals) / len(vals)) if vals else 0
        for name, vals in agent_tokens.items()
    }

    consistency_scores = [r["factual_consistency_score"] for r in successful if r["factual_consistency_score"] is not None]
    avg_consistency = round(sum(consistency_scores) / len(consistency_scores), 2) if consistency_scores else None

    return {
        "benchmark_config": {
            "company": company_name,
            "total_runs": total_runs,
            "sdk": "Claude Agent SDK",
        },
        "handoff_results": {
            "success_count": success_count,
            "failure_count": len(failed),
            "handoff_success_rate_pct": handoff_success_rate,
            "target_pct": 95.0,
            "passed": handoff_success_rate >= 95.0,
        },
        "token_efficiency": {
            "avg_tokens_per_run": avg_tokens,
            "avg_cost_per_run_usd": avg_cost,
            "tokens_per_agent": tokens_per_agent,
        },
        "timing": {
            "avg_time_per_run_s": avg_time,
        },
        "memory_state": {
            "avg_factual_consistency_score": avg_consistency,
        },
        "runs": results,
    }


def _save_reports(report: dict):
    """Save benchmark report as both JSON and Markdown."""
    os.makedirs("output", exist_ok=True)

    # JSON report
    json_path = "output/benchmark_report.json"
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)
    logger.info("Saved JSON report: %s", json_path)

    # Markdown report
    md_path = "output/benchmark_report.md"
    md = _render_markdown(report)
    with open(md_path, "w") as f:
        f.write(md)
    logger.info("Saved Markdown report: %s", md_path)


def _render_markdown(report: dict) -> str:
    """Render benchmark report as Markdown."""
    cfg = report["benchmark_config"]
    h = report["handoff_results"]
    t = report["token_efficiency"]
    tm = report["timing"]
    m = report["memory_state"]

    lines = [
        f"# Benchmark Report: {cfg['sdk']}",
        "",
        f"**Company:** {cfg['company']}  ",
        f"**Total Runs:** {cfg['total_runs']}  ",
        "",
        "## Handoff Results",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Success Count | {h['success_count']} |",
        f"| Failure Count | {h['failure_count']} |",
        f"| Success Rate | {h['handoff_success_rate_pct']}% |",
        f"| Target | {h['target_pct']}% |",
        f"| Passed | {'Yes' if h['passed'] else 'No'} |",
        "",
        "## Token Efficiency",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Avg Tokens/Run | {t['avg_tokens_per_run']:,} |",
        f"| Avg Cost/Run | ${t['avg_cost_per_run_usd']:.4f} |",
        "",
        "### Tokens per Agent",
        "",
        "| Agent | Avg Tokens |",
        "|-------|------------|",
    ]

    for agent, tokens in t["tokens_per_agent"].items():
        lines.append(f"| {agent} | {tokens:,} |")

    lines.extend([
        "",
        "## Timing",
        "",
        f"**Avg Time/Run:** {tm['avg_time_per_run_s']}s",
        "",
        "## Memory / State",
        "",
        f"**Avg Factual Consistency Score:** {m['avg_factual_consistency_score']}",
        "",
        "## Per-Run Details",
        "",
        "| Run | Success | Time (s) | Tokens | Cost ($) | Consistency |",
        "|-----|---------|----------|--------|----------|-------------|",
    ])

    for r in report["runs"]:
        lines.append(
            f"| {r['run_id']} | {'Pass' if r['handoff_success'] else 'Fail'} | "
            f"{r['total_time_s']} | {r['total_tokens']:,} | "
            f"${r['cost_usd']:.4f} | {r['factual_consistency_score'] or 'N/A'} |"
        )

    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    company = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_COMPANY
    num = int(sys.argv[2]) if len(sys.argv) > 2 else NUM_RUNS

    report = asyncio.run(run_benchmark(company, num))

    print(f"\nBenchmark complete: {report['handoff_results']['handoff_success_rate_pct']}% success rate")
    print(f"Reports saved to output/benchmark_report.json and output/benchmark_report.md")
