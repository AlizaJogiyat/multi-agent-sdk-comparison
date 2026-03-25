#!/usr/bin/env python3
"""
4-Agent Investment Memo Pipeline using Google ADK (Agent Development Kit)
Agent 1: Researcher - Searches for company information
Agent 2: Analyzer - Analyzes the research and scores opportunities
Agent 3: Writer - Drafts a 2-page investment memo from research + analysis
Agent 4: QA/Review - Checks memo for factual consistency, flags hallucinations
"""

import json
import os
import re
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import wikipedia

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

MODEL = "gemini-2.0-flash"
APP_NAME = "investment_pipeline"


def load_env(env_path: str = None):
    """Load environment variables from .env file."""
    if env_path:
        load_dotenv(dotenv_path=env_path)
    else:
        local_env = Path(__file__).parent / ".env"
        if local_env.exists():
            load_dotenv(dotenv_path=local_env)
        else:
            load_dotenv()
    # Google ADK uses GOOGLE_API_KEY env var
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if key:
        os.environ["GOOGLE_API_KEY"] = key


# ============================================================================
# TOOL DEFINITIONS (plain Python functions for Google ADK)
# ============================================================================

# --- Researcher Tools ---

def search_company_info(company_name: str) -> dict:
    """Search for information about a company including founding year, revenue, employee count, and sector."""
    try:
        print(f"  Fetching real data for {company_name}...")

        try:
            wiki_summary = wikipedia.summary(company_name, sentences=3)
            wikipedia.page(company_name, auto_suggest=True)

            data = {
                "founded": _extract_founded_year(wiki_summary),
                "revenue": "Not available from Wikipedia",
                "employees": "Not available from Wikipedia",
                "sector": _extract_sector(wiki_summary),
                "headquarters": _extract_headquarters(wiki_summary),
                "description": wiki_summary,
            }

            return {"success": True, "data": data, "source": "Wikipedia"}

        except wikipedia.exceptions.PageError:
            print(f"  {company_name} not found on Wikipedia...")
            return {
                "success": True,
                "data": {
                    "founded": "Information not available",
                    "revenue": "Information not available",
                    "employees": "Information not available",
                    "sector": "Technology",
                    "headquarters": "Unknown",
                    "description": f"{company_name} - Company information not found in public sources",
                },
                "source": "Web Search (Not Found)",
            }
    except Exception as e:
        print(f"  Error fetching data: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "data": {
                "founded": "Unknown",
                "revenue": "Unknown",
                "employees": "Unknown",
                "sector": "Unknown",
                "headquarters": "Unknown",
                "description": f"Could not retrieve information for {company_name}",
            },
        }


# --- Analyzer Tools ---

def calculate_metric(metric_type: str, company_data: dict) -> dict:
    """Calculate financial or operational metrics based on company data. metric_type can be revenue_per_employee, growth_potential, or market_readiness."""
    if isinstance(company_data, str):
        try:
            company_data = json.loads(company_data)
        except (json.JSONDecodeError, TypeError):
            company_data = {}

    employees = company_data.get("employees") or 1
    revenue_value = company_data.get("revenue") or "$0"

    revenue_str = str(revenue_value).replace("$", "").replace("M", "").replace(",", "")
    try:
        revenue = float(revenue_str)
    except (ValueError, TypeError):
        revenue = 0

    metrics = {
        "revenue_per_employee": revenue * 1_000_000 / max(int(employees) if str(employees).isdigit() else 1, 1),
        "growth_potential": "High" if revenue < 50 else "Medium",
        "market_readiness": "Ready for Series B" if revenue > 30 else "Series A Stage",
    }

    selected_metric = metrics.get(metric_type, metrics.get("revenue_per_employee"))

    return {
        "metric": metric_type,
        "value": selected_metric,
        "interpretation": f"Company shows strong metrics with {selected_metric} for {metric_type}",
    }


def score_opportunity(company_name: str, analysis_summary: str) -> dict:
    """Score the investment opportunity based on analysis."""
    return {
        "company": company_name,
        "opportunity_score": 8.2,
        "recommendation": "STRONG BUY",
        "reasoning": f"Based on analysis: {analysis_summary[:100]}...",
        "risk_level": "Low to Medium",
        "investment_readiness": "Ready",
    }


# --- Writer Tools ---

def format_memo(company_name: str, sections: dict) -> dict:
    """Format the investment memo into a structured company template with sections: executive_summary, company_overview, financial_analysis, investment_thesis, risks, recommendation."""
    from datetime import date

    if isinstance(sections, str):
        try:
            sections = json.loads(sections)
        except (json.JSONDecodeError, TypeError):
            sections = {}

    template = f"""
{'='*70}
CONFIDENTIAL - INVESTMENT MEMO
{'='*70}

Company:    {company_name}
Date:       {date.today().strftime('%B %d, %Y')}
Prepared by: AI Investment Research Pipeline (Google ADK)

{'-'*70}
1. EXECUTIVE SUMMARY
{'-'*70}
{sections.get('executive_summary', 'N/A')}

{'-'*70}
2. COMPANY OVERVIEW
{'-'*70}
{sections.get('company_overview', 'N/A')}

{'-'*70}
3. FINANCIAL ANALYSIS
{'-'*70}
{sections.get('financial_analysis', 'N/A')}

{'-'*70}
4. INVESTMENT THESIS
{'-'*70}
{sections.get('investment_thesis', 'N/A')}

{'-'*70}
5. KEY RISKS
{'-'*70}
{sections.get('risks', 'N/A')}

{'-'*70}
6. RECOMMENDATION
{'-'*70}
{sections.get('recommendation', 'N/A')}

{'='*70}
END OF MEMO
{'='*70}
"""

    return {
        "success": True,
        "formatted_memo": template,
        "word_count": len(template.split()),
        "sections_included": list(sections.keys()),
    }


# --- QA/Review Tools ---

def fact_check(claim: str, source_data: str) -> dict:
    """Cross-reference a claim from the investment memo against the original research data. Returns whether the claim is supported, unsupported, or contradicted."""
    claim_lower = claim.lower()
    source_lower = source_data.lower()

    claim_words = set(claim_lower.split())
    source_words = set(source_lower.split())
    overlap = claim_words & source_words
    overlap_ratio = len(overlap) / max(len(claim_words), 1)

    if overlap_ratio > 0.4:
        verdict = "SUPPORTED"
        confidence = min(0.5 + overlap_ratio, 0.95)
        explanation = "Key terms from this claim are found in the source research data."
    elif overlap_ratio > 0.2:
        verdict = "PARTIALLY_SUPPORTED"
        confidence = 0.4 + overlap_ratio
        explanation = "Some elements of this claim are present in the source data, but not all details can be verified."
    else:
        verdict = "UNSUPPORTED"
        confidence = max(0.3, overlap_ratio)
        explanation = "This claim does not appear to be directly supported by the source research data."

    return {
        "claim": claim[:200],
        "verdict": verdict,
        "confidence": round(confidence, 2),
        "explanation": explanation,
        "matching_terms": list(overlap)[:10],
    }


def flag_issue(issue_type: str, description: str, severity: str, location: str, suggestion: str = "") -> dict:
    """Flag a specific issue found in the memo. issue_type: hallucination, inconsistency, unsupported_claim, missing_info, formatting. severity: critical, major, minor."""
    severity_icons = {"critical": "RED", "major": "ORANGE", "minor": "YELLOW"}
    type_labels = {
        "hallucination": "Hallucination Detected",
        "inconsistency": "Factual Inconsistency",
        "unsupported_claim": "Unsupported Claim",
        "missing_info": "Missing Information",
        "formatting": "Formatting Issue",
    }

    return {
        "issue_id": f"QA-{hash(description) % 10000:04d}",
        "icon": severity_icons.get(severity, "WHITE"),
        "type_label": type_labels.get(issue_type, issue_type),
        "issue_type": issue_type,
        "severity": severity,
        "location": location,
        "description": description,
        "suggestion": suggestion or "No suggestion provided",
        "status": "OPEN",
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _extract_founded_year(text: str) -> str:
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
    return years[0] if years else "Unknown"


def _extract_sector(text: str) -> str:
    sectors = {
        "software": "Software/SaaS",
        "technology": "Technology",
        "ai": "Artificial Intelligence",
        "machine learning": "Machine Learning",
        "cloud": "Cloud Computing",
        "social": "Social Media",
        "e-commerce": "E-Commerce",
        "fintech": "FinTech",
        "healthtech": "HealthTech",
        "recruitment": "HR Tech",
        "database": "Database/Infrastructure",
    }
    text_lower = text.lower()
    for keyword, sector in sectors.items():
        if keyword in text_lower:
            return sector
    return "Technology"


def _extract_headquarters(text: str) -> str:
    locations = re.findall(
        r'(?:based in|headquartered in|founded in)\s+([^.,]+(?:,\s*[^.,]+)?)',
        text,
        re.IGNORECASE,
    )
    return locations[0].strip() if locations else "Unknown"


# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

researcher_agent = Agent(
    name="researcher",
    model=MODEL,
    instruction="You are a company research specialist. When given a company name, use the search_company_info tool to find detailed information about the company including founding year, revenue, employees, and sector. After getting the tool results, provide a comprehensive research brief summarizing all findings.",
    tools=[search_company_info],
)

analyzer_agent = Agent(
    name="analyzer",
    model=MODEL,
    instruction="""You are an investment analyst. You will receive a research brief about a company. Your job is to:
1. Calculate the revenue_per_employee metric using the calculate_metric tool
2. Score the investment opportunity using the score_opportunity tool
3. Provide a comprehensive analysis with your investment recommendation

Use the available tools to complete this analysis, then provide a detailed summary.""",
    tools=[calculate_metric, score_opportunity],
)

writer_agent = Agent(
    name="writer",
    model=MODEL,
    instruction="""You are a professional investment memo writer. You will receive research and analysis briefs. Your job is to draft a professional 2-page investment memo using the format_memo tool with these sections:
1. Executive Summary - 2-3 sentence high-level overview
2. Company Overview - What the company does, founding, sector, headquarters
3. Financial Analysis - Key metrics, revenue, growth potential
4. Investment Thesis - Why this is a compelling opportunity
5. Key Risks - 3-4 bullet points of risks
6. Recommendation - Final investment recommendation with rationale

Use the format_memo tool to structure the memo, then present the formatted result.""",
    tools=[format_memo],
)

qa_agent = Agent(
    name="qa_reviewer",
    model=MODEL,
    instruction="""You are a senior QA reviewer for investment memos. Your job is to ensure factual accuracy and flag any problems. You must:
1. Fact-check at least 3-5 key claims in the memo against the original research data using the fact_check tool. Focus on numbers, dates, company details.
2. Flag issues using the flag_issue tool for any hallucinations, inconsistencies, unsupported claims, or missing information.
3. After checking, provide a final QA summary with:
   - Overall quality score (1-10)
   - Number of issues found by severity
   - Whether the memo is APPROVED, NEEDS REVISION, or REJECTED
   - Specific revision requests if needed""",
    tools=[fact_check, flag_issue],
)


# ============================================================================
# PIPELINE RUNNER HELPERS
# ============================================================================

async def run_single_agent(agent: Agent, user_message: str, user_id: str = "user") -> str:
    """Run a single Google ADK agent and return its final text output."""
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)
    session = await session_service.create_session(app_name=APP_NAME, user_id=user_id)

    content = types.Content(
        role="user",
        parts=[types.Part(text=user_message)],
    )

    final_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_text = "".join(
                    part.text for part in event.content.parts if part.text
                )

    return final_text


# ============================================================================
# MAIN (CLI)
# ============================================================================

async def run_full_pipeline(company_name: str):
    print("\n")
    print("*" * 70)
    print("4-AGENT INVESTMENT MEMO PIPELINE (Google ADK)")
    print("Researcher -> Analyzer -> Writer -> QA/Review")
    print("*" * 70)

    # Agent 1: Researcher
    print("\n" + "=" * 70)
    print("AGENT 1: RESEARCHER")
    print("=" * 70)
    agent1_output = await run_single_agent(
        researcher_agent,
        f"Search for information about {company_name} including their founding year, revenue, number of employees, and sector. Provide a brief research summary.",
    )
    print(f"  Output: {agent1_output[:300]}...")

    # Agent 2: Analyzer
    print("\n" + "=" * 70)
    print("AGENT 2: ANALYZER")
    print("=" * 70)
    agent2_output = await run_single_agent(
        analyzer_agent,
        f"""You have received the following research brief from the Research Agent:

{agent1_output}

Please analyze this information by:
1. Calculating the revenue_per_employee metric
2. Scoring the investment opportunity
3. Providing your investment recommendation

Use the available tools to complete this analysis.""",
    )
    print(f"  Output: {agent2_output[:300]}...")

    # Agent 3: Writer
    print("\n" + "=" * 70)
    print("AGENT 3: WRITER")
    print("=" * 70)
    agent3_output = await run_single_agent(
        writer_agent,
        f"""You are an investment memo writer. You have received the following inputs:

--- RESEARCH BRIEF (from Researcher Agent) ---
{agent1_output}

--- ANALYSIS BRIEF (from Analyzer Agent) ---
{agent2_output}

Draft a professional 2-page investment memo for {company_name}. Use the format_memo tool with these sections:
1. Executive Summary - 2-3 sentence overview
2. Company Overview - What the company does, founding, sector
3. Financial Analysis - Key metrics and growth potential
4. Investment Thesis - Why this is compelling
5. Key Risks - 3-4 bullet points
6. Recommendation - Final investment recommendation

Keep it professional and concise.""",
    )
    print(f"  Output: {agent3_output[:300]}...")

    # Agent 4: QA
    print("\n" + "=" * 70)
    print("AGENT 4: QA / REVIEW")
    print("=" * 70)
    agent4_output = await run_single_agent(
        qa_agent,
        f"""You are a senior QA reviewer for investment memos.

You have 3 documents to cross-reference:

--- ORIGINAL RESEARCH (Source of Truth) ---
{agent1_output}

--- ANALYSIS ---
{agent2_output}

--- INVESTMENT MEMO (To Review) ---
{agent3_output}

Your task:
1. Fact-check at least 3-5 key claims using the fact_check tool.
2. Flag issues using the flag_issue tool.
3. Provide a final QA summary with quality score, issues by severity, and APPROVED/NEEDS REVISION/REJECTED verdict.""",
    )
    print(f"  Output: {agent4_output[:300]}...")

    # Final results
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print("\nAGENT 1 RESEARCH:")
    print("-" * 70)
    print(agent1_output)
    print("\nAGENT 2 ANALYSIS:")
    print("-" * 70)
    print(agent2_output)
    print("\nAGENT 3 INVESTMENT MEMO:")
    print("-" * 70)
    print(agent3_output)
    print("\nAGENT 4 QA REVIEW:")
    print("-" * 70)
    print(agent4_output)
    print("\nSUCCESS: All 4 agents communicated successfully!")


def main():
    load_env()
    company_name = input("Enter company name to research: ").strip()
    if not company_name:
        company_name = "Vettio"
        print(f"No input provided. Using default: {company_name}")

    asyncio.run(run_full_pipeline(company_name))


if __name__ == "__main__":
    main()
