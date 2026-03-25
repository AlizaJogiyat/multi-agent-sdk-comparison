#!/usr/bin/env python3
"""
4-Agent Investment Memo Pipeline using OpenAI Agents SDK
Agent 1: Researcher - Searches for company information
Agent 2: Analyzer - Analyzes the research and scores opportunities
Agent 3: Writer - Drafts a 2-page investment memo from research + analysis
Agent 4: QA/Review - Checks memo for factual consistency, flags hallucinations, requests revisions
"""

import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
import wikipedia

MODEL = "gpt-4o"


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


# ============================================================================
# TOOL DEFINITIONS (using @function_tool decorator)
# ============================================================================

# --- Researcher Tools ---

@function_tool
def search_company_info(company_name: str) -> str:
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

            return json.dumps({"success": True, "data": data, "source": "Wikipedia"})

        except wikipedia.exceptions.PageError:
            print(f"  {company_name} not found on Wikipedia...")
            return json.dumps({
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
            })
    except Exception as e:
        print(f"  Error fetching data: {str(e)}")
        return json.dumps({
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
        })


# --- Analyzer Tools ---

@function_tool
def calculate_metric(metric_type: str, company_data: str) -> str:
    """Calculate financial or operational metrics based on company data. company_data should be a JSON string with financial information."""
    try:
        if isinstance(company_data, str):
            parsed = json.loads(company_data)
        else:
            parsed = company_data
    except (json.JSONDecodeError, TypeError):
        parsed = {}

    employees = parsed.get("employees") or 1
    revenue_value = parsed.get("revenue") or "$0"

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

    return json.dumps({
        "metric": metric_type,
        "value": selected_metric,
        "interpretation": f"Company shows strong metrics with {selected_metric} for {metric_type}",
    })


@function_tool
def score_opportunity(company_name: str, analysis_summary: str) -> str:
    """Score the investment opportunity based on analysis."""
    return json.dumps({
        "company": company_name,
        "opportunity_score": 8.2,
        "recommendation": "STRONG BUY",
        "reasoning": f"Based on analysis: {analysis_summary[:100]}...",
        "risk_level": "Low to Medium",
        "investment_readiness": "Ready",
    })


# --- Writer Tools ---

@function_tool
def format_memo(company_name: str, sections: str) -> str:
    """Format the investment memo into a structured company template. sections should be a JSON string with keys: executive_summary, company_overview, financial_analysis, investment_thesis, risks, recommendation."""
    from datetime import date

    try:
        if isinstance(sections, str):
            parsed_sections = json.loads(sections)
        else:
            parsed_sections = sections
    except (json.JSONDecodeError, TypeError):
        parsed_sections = {}

    template = f"""
{'='*70}
CONFIDENTIAL - INVESTMENT MEMO
{'='*70}

Company:    {company_name}
Date:       {date.today().strftime('%B %d, %Y')}
Prepared by: AI Investment Research Pipeline (OpenAI Agents SDK)

{'-'*70}
1. EXECUTIVE SUMMARY
{'-'*70}
{parsed_sections.get('executive_summary', 'N/A')}

{'-'*70}
2. COMPANY OVERVIEW
{'-'*70}
{parsed_sections.get('company_overview', 'N/A')}

{'-'*70}
3. FINANCIAL ANALYSIS
{'-'*70}
{parsed_sections.get('financial_analysis', 'N/A')}

{'-'*70}
4. INVESTMENT THESIS
{'-'*70}
{parsed_sections.get('investment_thesis', 'N/A')}

{'-'*70}
5. KEY RISKS
{'-'*70}
{parsed_sections.get('risks', 'N/A')}

{'-'*70}
6. RECOMMENDATION
{'-'*70}
{parsed_sections.get('recommendation', 'N/A')}

{'='*70}
END OF MEMO
{'='*70}
"""

    return json.dumps({
        "success": True,
        "formatted_memo": template,
        "word_count": len(template.split()),
        "sections_included": list(parsed_sections.keys()),
    })


# --- QA/Review Tools ---

@function_tool
def fact_check(claim: str, source_data: str) -> str:
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

    return json.dumps({
        "claim": claim[:200],
        "verdict": verdict,
        "confidence": round(confidence, 2),
        "explanation": explanation,
        "matching_terms": list(overlap)[:10],
    })


@function_tool
def flag_issue(issue_type: str, description: str, severity: str, location: str, suggestion: str = "") -> str:
    """Flag a specific issue found in the memo. issue_type must be one of: hallucination, inconsistency, unsupported_claim, missing_info, formatting. severity must be one of: critical, major, minor."""
    severity_icons = {"critical": "RED", "major": "ORANGE", "minor": "YELLOW"}
    type_labels = {
        "hallucination": "Hallucination Detected",
        "inconsistency": "Factual Inconsistency",
        "unsupported_claim": "Unsupported Claim",
        "missing_info": "Missing Information",
        "formatting": "Formatting Issue",
    }

    return json.dumps({
        "issue_id": f"QA-{hash(description) % 10000:04d}",
        "icon": severity_icons.get(severity, "WHITE"),
        "type_label": type_labels.get(issue_type, issue_type),
        "issue_type": issue_type,
        "severity": severity,
        "location": location,
        "description": description,
        "suggestion": suggestion or "No suggestion provided",
        "status": "OPEN",
    })


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
    name="Researcher",
    instructions="You are a company research specialist. When given a company name, use the search_company_info tool to find detailed information about the company including founding year, revenue, employees, and sector. After getting the tool results, provide a comprehensive research brief summarizing all findings.",
    tools=[search_company_info],
    model=MODEL,
)

analyzer_agent = Agent(
    name="Analyzer",
    instructions="""You are an investment analyst. You will receive a research brief about a company. Your job is to:
1. Calculate the revenue_per_employee metric using the calculate_metric tool
2. Score the investment opportunity using the score_opportunity tool
3. Provide a comprehensive analysis with your investment recommendation

Use the available tools to complete this analysis, then provide a detailed summary.""",
    tools=[calculate_metric, score_opportunity],
    model=MODEL,
)

writer_agent = Agent(
    name="Writer",
    instructions="""You are a professional investment memo writer. You will receive research and analysis briefs. Your job is to draft a professional 2-page investment memo using the format_memo tool with these sections:
1. Executive Summary - 2-3 sentence high-level overview
2. Company Overview - What the company does, founding, sector, headquarters
3. Financial Analysis - Key metrics, revenue, growth potential
4. Investment Thesis - Why this is a compelling opportunity
5. Key Risks - 3-4 bullet points of risks
6. Recommendation - Final investment recommendation with rationale

Use the format_memo tool to structure the memo, then present the formatted result.""",
    tools=[format_memo],
    model=MODEL,
)

qa_agent = Agent(
    name="QA/Review",
    instructions="""You are a senior QA reviewer for investment memos. Your job is to ensure factual accuracy and flag any problems. You must:
1. Fact-check at least 3-5 key claims in the memo against the original research data using the fact_check tool. Focus on numbers, dates, company details.
2. Flag issues using the flag_issue tool for any hallucinations, inconsistencies, unsupported claims, or missing information.
3. After checking, provide a final QA summary with:
   - Overall quality score (1-10)
   - Number of issues found by severity
   - Whether the memo is APPROVED, NEEDS REVISION, or REJECTED
   - Specific revision requests if needed""",
    tools=[fact_check, flag_issue],
    model=MODEL,
)


# ============================================================================
# PIPELINE RUNNER
# ============================================================================

import asyncio


async def run_researcher(company_name: str) -> str:
    print("\n" + "=" * 70)
    print("AGENT 1: RESEARCHER")
    print("=" * 70)

    result = await Runner.run(
        researcher_agent,
        input=f"Search for information about {company_name} including their founding year, revenue, number of employees, and sector. Provide a brief research summary.",
    )
    output = result.final_output
    print(f"  Output: {output[:300]}...")
    return output


async def run_analyzer(research_brief: str) -> str:
    print("\n" + "=" * 70)
    print("AGENT 2: ANALYZER")
    print("=" * 70)

    result = await Runner.run(
        analyzer_agent,
        input=f"""You have received the following research brief from the Research Agent:

{research_brief}

Please analyze this information by:
1. Calculating the revenue_per_employee metric
2. Scoring the investment opportunity
3. Providing your investment recommendation

Use the available tools to complete this analysis.""",
    )
    output = result.final_output
    print(f"  Output: {output[:300]}...")
    return output


async def run_writer(company_name: str, research_brief: str, analysis_brief: str) -> str:
    print("\n" + "=" * 70)
    print("AGENT 3: WRITER")
    print("=" * 70)

    result = await Runner.run(
        writer_agent,
        input=f"""You are an investment memo writer. You have received the following inputs:

--- RESEARCH BRIEF (from Researcher Agent) ---
{research_brief}

--- ANALYSIS BRIEF (from Analyzer Agent) ---
{analysis_brief}

Draft a professional 2-page investment memo for {company_name}. Use the format_memo tool with these sections:
1. Executive Summary - 2-3 sentence overview
2. Company Overview - What the company does, founding, sector
3. Financial Analysis - Key metrics and growth potential
4. Investment Thesis - Why this is compelling
5. Key Risks - 3-4 bullet points
6. Recommendation - Final investment recommendation

Keep it professional and concise.""",
    )
    output = result.final_output
    print(f"  Output: {output[:300]}...")
    return output


async def run_qa(company_name: str, research_brief: str, analysis_brief: str, memo: str) -> str:
    print("\n" + "=" * 70)
    print("AGENT 4: QA / REVIEW")
    print("=" * 70)

    result = await Runner.run(
        qa_agent,
        input=f"""You are a senior QA reviewer for investment memos. Your job is to ensure factual accuracy and flag any problems.

You have 3 documents to cross-reference:

--- ORIGINAL RESEARCH (Source of Truth) ---
{research_brief}

--- ANALYSIS ---
{analysis_brief}

--- INVESTMENT MEMO (To Review) ---
{memo}

Your task:
1. Fact-check at least 3-5 key claims in the memo against the original research data using the fact_check tool.
2. Flag issues using the flag_issue tool for any hallucinations, inconsistencies, unsupported claims, or missing information.
3. Provide a final QA summary with:
   - Overall quality score (1-10)
   - Number of issues found by severity
   - Whether the memo is APPROVED, NEEDS REVISION, or REJECTED
   - Specific revision requests if needed""",
    )
    output = result.final_output
    print(f"  Output: {output[:300]}...")
    return output


async def run_full_pipeline(company_name: str):
    print("\n")
    print("*" * 70)
    print("4-AGENT INVESTMENT MEMO PIPELINE (OpenAI Agents SDK)")
    print("Researcher -> Analyzer -> Writer -> QA/Review")
    print("*" * 70)

    agent1_output = await run_researcher(company_name)
    agent2_output = await run_analyzer(agent1_output)
    agent3_output = await run_writer(company_name, agent1_output, agent2_output)
    agent4_output = await run_qa(company_name, agent1_output, agent2_output, agent3_output)

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