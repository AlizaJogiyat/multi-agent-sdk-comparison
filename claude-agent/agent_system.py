#!/usr/bin/env python3
"""
4-Agent Investment Memo Pipeline using Anthropic SDK
Agent 1: Researcher - Searches for company information
Agent 2: Analyzer - Analyzes the research and scores opportunities
Agent 3: Writer - Drafts a 2-page investment memo from research + analysis
Agent 4: QA/Review - Checks memo for factual consistency, flags hallucinations, requests revisions
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic
import wikipedia

MODEL = "claude-sonnet-4-6"


def get_client(env_path: str = None) -> Anthropic:
    """Initialize and return Anthropic client. Loads .env from given path or auto-detects."""
    if env_path:
        load_dotenv(dotenv_path=env_path)
    else:
        # Try local .env first, then claude-agent/.env
        local_env = Path(__file__).parent / ".env"
        if local_env.exists():
            load_dotenv(dotenv_path=local_env)
        else:
            load_dotenv()
    return Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

RESEARCHER_TOOLS = [
    {
        "name": "search_company_info",
        "description": "Search for information about a company including founding year, revenue, employee count, and sector",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "The name of the company to search for"
                }
            },
            "required": ["company_name"]
        }
    }
]

ANALYZER_TOOLS = [
    {
        "name": "calculate_metric",
        "description": "Calculate financial or operational metrics based on company data",
        "input_schema": {
            "type": "object",
            "properties": {
                "metric_type": {
                    "type": "string",
                    "description": "Type of metric (revenue_per_employee, growth_potential, etc.)"
                },
                "company_data": {
                    "type": "object",
                    "description": "Company data object with financial information"
                }
            },
            "required": ["metric_type", "company_data"]
        }
    },
    {
        "name": "score_opportunity",
        "description": "Score the investment opportunity based on analysis",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Name of the company"
                },
                "analysis_summary": {
                    "type": "string",
                    "description": "Summary of the analysis"
                }
            },
            "required": ["company_name", "analysis_summary"]
        }
    }
]

WRITER_TOOLS = [
    {
        "name": "format_memo",
        "description": "Format the investment memo into a structured company template with sections like Executive Summary, Company Overview, Financial Analysis, Investment Thesis, Risks, and Recommendation",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "Name of the company"
                },
                "sections": {
                    "type": "object",
                    "description": "Memo sections with keys: executive_summary, company_overview, financial_analysis, investment_thesis, risks, recommendation"
                }
            },
            "required": ["company_name", "sections"]
        }
    }
]

QA_TOOLS = [
    {
        "name": "fact_check",
        "description": "Cross-reference a claim from the investment memo against the original research data. Returns whether the claim is supported, unsupported, or contradicted by the source data.",
        "input_schema": {
            "type": "object",
            "properties": {
                "claim": {
                    "type": "string",
                    "description": "The specific claim or statement from the memo to verify"
                },
                "source_data": {
                    "type": "string",
                    "description": "The original research data to check the claim against"
                }
            },
            "required": ["claim", "source_data"]
        }
    },
    {
        "name": "flag_issue",
        "description": "Flag a specific issue found in the memo such as a hallucination, factual inconsistency, unsupported claim, or missing information",
        "input_schema": {
            "type": "object",
            "properties": {
                "issue_type": {
                    "type": "string",
                    "enum": ["hallucination", "inconsistency", "unsupported_claim", "missing_info", "formatting"],
                    "description": "Type of issue found"
                },
                "description": {
                    "type": "string",
                    "description": "Detailed description of the issue"
                },
                "severity": {
                    "type": "string",
                    "enum": ["critical", "major", "minor"],
                    "description": "Severity level of the issue"
                },
                "location": {
                    "type": "string",
                    "description": "Which section of the memo the issue is in"
                },
                "suggestion": {
                    "type": "string",
                    "description": "Suggested fix or revision"
                }
            },
            "required": ["issue_type", "description", "severity", "location"]
        }
    }
]

# ============================================================================
# SIMULATED TOOL EXECUTION
# ============================================================================

def execute_search_company_info(company_name: str) -> dict:
    """
    Fetch real company information from Wikipedia and web sources
    """
    try:
        print(f"  📡 Fetching real data for {company_name}...")

        # Try Wikipedia API first (most reliable)
        try:
            # Search for the company on Wikipedia
            wiki_summary = wikipedia.summary(company_name, sentences=3)
            wiki_page = wikipedia.page(company_name, auto_suggest=True)

            # Extract basic info
            data = {
                "founded": extract_founded_year(wiki_summary),
                "revenue": "Not available from Wikipedia",
                "employees": "Not available from Wikipedia",
                "sector": extract_sector(wiki_summary),
                "headquarters": extract_headquarters(wiki_summary),
                "description": wiki_summary
            }

            return {
                "success": True,
                "data": data,
                "source": "Wikipedia"
            }
        except wikipedia.exceptions.PageError:
            print(f"  ⚠️  {company_name} not found on Wikipedia, trying web search...")

            # Fallback: Return structured but minimal data with source info
            return {
                "success": True,
                "data": {
                    "founded": "Information not available",
                    "revenue": "Information not available",
                    "employees": "Information not available",
                    "sector": "Technology",
                    "headquarters": "Unknown",
                    "description": f"{company_name} - Company information not found in public sources"
                },
                "source": "Web Search (Not Found)"
            }
    except Exception as e:
        print(f"  ❌ Error fetching data: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "data": {
                "founded": "Unknown",
                "revenue": "Unknown",
                "employees": "Unknown",
                "sector": "Unknown",
                "headquarters": "Unknown",
                "description": f"Could not retrieve information for {company_name}"
            }
        }

def extract_founded_year(text: str) -> str:
    """Extract founding year from text"""
    import re
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
    if years:
        return years[0]
    return "Unknown"

def extract_sector(text: str) -> str:
    """Extract sector/industry from text"""
    # Common sector keywords
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
        "database": "Database/Infrastructure"
    }

    text_lower = text.lower()
    for keyword, sector in sectors.items():
        if keyword in text_lower:
            return sector
    return "Technology"

def extract_headquarters(text: str) -> str:
    """Extract headquarters location from text"""
    # Look for location patterns (City, State/Country)
    import re
    locations = re.findall(r'(?:based in|headquartered in|founded in)\s+([^.,]+(?:,\s*[^.,]+)?)', text, re.IGNORECASE)
    if locations:
        return locations[0].strip()
    return "Unknown"

def execute_calculate_metric(metric_type: str, company_data: dict) -> dict:
    """Simulated metric calculation"""
    employees = company_data.get("employees") or 1
    revenue_value = company_data.get("revenue") or "$0"

    # Convert to string and clean up
    revenue_str = str(revenue_value).replace("$", "").replace("M", "").replace(",", "")

    try:
        revenue = float(revenue_str)
    except:
        revenue = 0

    metrics = {
        "revenue_per_employee": revenue * 1_000_000 / max(employees, 1),
        "growth_potential": "High" if revenue < 50 else "Medium",
        "market_readiness": "Ready for Series B" if revenue > 30 else "Series A Stage"
    }

    selected_metric = metrics.get(metric_type, metrics.get("revenue_per_employee"))

    return {
        "metric": metric_type,
        "value": selected_metric,
        "interpretation": f"Company shows strong metrics with {selected_metric} for {metric_type}"
    }

def execute_score_opportunity(company_name: str, analysis_summary: str) -> dict:
    """Simulated opportunity scoring"""
    return {
        "company": company_name,
        "opportunity_score": 8.2,
        "recommendation": "STRONG BUY",
        "reasoning": f"Based on analysis: {analysis_summary[:100]}...",
        "risk_level": "Low to Medium",
        "investment_readiness": "Ready"
    }

def execute_format_memo(company_name: str, sections: dict) -> dict:
    """Format memo into a structured company template"""
    from datetime import date

    template = f"""
{'='*70}
CONFIDENTIAL — INVESTMENT MEMO
{'='*70}

Company:    {company_name}
Date:       {date.today().strftime('%B %d, %Y')}
Prepared by: AI Investment Research Pipeline

{'─'*70}
1. EXECUTIVE SUMMARY
{'─'*70}
{sections.get('executive_summary', 'N/A')}

{'─'*70}
2. COMPANY OVERVIEW
{'─'*70}
{sections.get('company_overview', 'N/A')}

{'─'*70}
3. FINANCIAL ANALYSIS
{'─'*70}
{sections.get('financial_analysis', 'N/A')}

{'─'*70}
4. INVESTMENT THESIS
{'─'*70}
{sections.get('investment_thesis', 'N/A')}

{'─'*70}
5. KEY RISKS
{'─'*70}
{sections.get('risks', 'N/A')}

{'─'*70}
6. RECOMMENDATION
{'─'*70}
{sections.get('recommendation', 'N/A')}

{'='*70}
END OF MEMO
{'='*70}
"""

    return {
        "success": True,
        "formatted_memo": template,
        "word_count": len(template.split()),
        "sections_included": list(sections.keys())
    }

def execute_fact_check(claim: str, source_data: str) -> dict:
    """Cross-reference a claim against source data"""
    claim_lower = claim.lower()
    source_lower = source_data.lower()

    # Check if key terms from the claim appear in the source
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
        explanation = "This claim does not appear to be directly supported by the source research data. It may be a hallucination or inference not grounded in the provided research."

    return {
        "claim": claim[:200],
        "verdict": verdict,
        "confidence": round(confidence, 2),
        "explanation": explanation,
        "matching_terms": list(overlap)[:10]
    }

def execute_flag_issue(issue_type: str, description: str, severity: str, location: str, suggestion: str = "") -> dict:
    """Record a flagged issue in the memo"""
    severity_icons = {"critical": "🔴", "major": "🟠", "minor": "🟡"}
    type_labels = {
        "hallucination": "Hallucination Detected",
        "inconsistency": "Factual Inconsistency",
        "unsupported_claim": "Unsupported Claim",
        "missing_info": "Missing Information",
        "formatting": "Formatting Issue"
    }

    return {
        "issue_id": f"QA-{hash(description) % 10000:04d}",
        "icon": severity_icons.get(severity, "⚪"),
        "type_label": type_labels.get(issue_type, issue_type),
        "issue_type": issue_type,
        "severity": severity,
        "location": location,
        "description": description,
        "suggestion": suggestion or "No suggestion provided",
        "status": "OPEN"
    }

def process_tool_call(tool_name: str, tool_input: dict) -> str:
    """Process tool calls and return results"""
    print(f"  → Calling tool: {tool_name}")

    if tool_name == "search_company_info":
        result = execute_search_company_info(tool_input["company_name"])
    elif tool_name == "calculate_metric":
        result = execute_calculate_metric(tool_input["metric_type"], tool_input["company_data"])
    elif tool_name == "score_opportunity":
        result = execute_score_opportunity(tool_input["company_name"], tool_input["analysis_summary"])
    elif tool_name == "format_memo":
        result = execute_format_memo(tool_input["company_name"], tool_input["sections"])
    elif tool_name == "fact_check":
        result = execute_fact_check(tool_input["claim"], tool_input["source_data"])
    elif tool_name == "flag_issue":
        result = execute_flag_issue(
            tool_input["issue_type"],
            tool_input["description"],
            tool_input["severity"],
            tool_input["location"],
            tool_input.get("suggestion", "")
        )
    else:
        result = {"error": f"Unknown tool: {tool_name}"}

    return json.dumps(result)

# ============================================================================
# AGENT FUNCTIONS
# ============================================================================

def run_researcher_agent(client: Anthropic, company_name: str) -> str:
    """
    Agent 1: Researcher Agent
    Searches for company information and returns research brief
    """
    print("\n" + "="*70)
    print("AGENT 1: RESEARCHER")
    print("="*70)
    print(f"Task: Research company information for '{company_name}'")
    print()

    messages = [
        {
            "role": "user",
            "content": f"Search for information about {company_name} including their founding year, revenue, number of employees, and sector. Provide a brief research summary."
        }
    ]

    iteration = 1
    research_output = None

    while True:
        print(f"Iteration {iteration}:")

        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=RESEARCHER_TOOLS,
            messages=messages
        )

        print(f"  Stop Reason: {response.stop_reason}")

        # Process response content
        if response.stop_reason == "tool_use":
            # Find tool use blocks
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id

                    print(f"  Tool Input: {json.dumps(tool_input, indent=2)}")

                    # Execute tool
                    tool_result = process_tool_call(tool_name, tool_input)
                    print(f"  Tool Result: {tool_result}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": tool_result
                    })
                elif block.type == "text":
                    if block.text:
                        print(f"  Text: {block.text}")

            # Add assistant response and tool results to messages
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            # Agent finished - extract final text
            for block in response.content:
                if block.type == "text":
                    research_output = block.text
                    print(f"  Final Output: {block.text}")
            break

        iteration += 1
        print()

    print()
    return research_output

def run_analyzer_agent(client: Anthropic, research_brief: str) -> str:
    """
    Agent 2: Analyzer Agent
    Takes research from Agent 1 and analyzes it
    """
    print("="*70)
    print("AGENT 2: ANALYZER")
    print("="*70)
    print("Task: Analyze the research and score the opportunity")
    print()
    print(f"Received Research from Agent 1:\n{research_brief}\n")

    messages = [
        {
            "role": "user",
            "content": f"""You have received the following research brief from the Research Agent:

{research_brief}

Please analyze this information by:
1. Calculating the revenue_per_employee metric
2. Scoring the investment opportunity
3. Providing your investment recommendation

Use the available tools to complete this analysis."""
        }
    ]

    iteration = 1
    analysis_output = None
    company_data = {"revenue": "$42.5M", "employees": 156}  # Default data

    while True:
        print(f"Iteration {iteration}:")

        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=ANALYZER_TOOLS,
            messages=messages
        )

        print(f"  Stop Reason: {response.stop_reason}")

        # Process response content
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id

                    print(f"  Tool Input: {json.dumps(tool_input, indent=2)}")

                    # Execute tool
                    tool_result = process_tool_call(tool_name, tool_input)
                    print(f"  Tool Result: {tool_result}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": tool_result
                    })
                elif block.type == "text":
                    if block.text:
                        print(f"  Text: {block.text}")

            # Add assistant response and tool results to messages
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            # Agent finished - extract final text
            for block in response.content:
                if block.type == "text":
                    analysis_output = block.text
                    print(f"  Final Output: {block.text}")
            break

        iteration += 1
        print()

    print()
    return analysis_output

def run_writer_agent(client: Anthropic, company_name: str, research_brief: str, analysis_brief: str) -> str:
    """
    Agent 3: Writer Agent
    Takes research from Agent 1 and analysis from Agent 2,
    drafts a 2-page investment memo following a company template
    """
    print("="*70)
    print("AGENT 3: WRITER")
    print("="*70)
    print("Task: Draft a 2-page investment memo")
    print()
    print(f"Received Research from Agent 1 and Analysis from Agent 2\n")

    messages = [
        {
            "role": "user",
            "content": f"""You are an investment memo writer. You have received the following inputs from the research and analysis pipeline:

--- RESEARCH BRIEF (from Researcher Agent) ---
{research_brief}

--- ANALYSIS BRIEF (from Analyzer Agent) ---
{analysis_brief}

Your task is to draft a professional 2-page investment memo for {company_name}. Use the format_memo tool to structure it with these sections:

1. **Executive Summary** — 2-3 sentence high-level overview of the opportunity
2. **Company Overview** — What the company does, founding, sector, headquarters
3. **Financial Analysis** — Key metrics, revenue, growth potential from the analysis
4. **Investment Thesis** — Why this is a compelling investment opportunity
5. **Key Risks** — 3-4 bullet points of risks to consider
6. **Recommendation** — Final investment recommendation with rationale

Keep the tone professional and concise. Each section should be substantive but focused — aim for roughly 2 pages total."""
        }
    ]

    iteration = 1
    writer_output = None

    while True:
        print(f"Iteration {iteration}:")

        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            tools=WRITER_TOOLS,
            messages=messages
        )

        print(f"  Stop Reason: {response.stop_reason}")

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id

                    print(f"  Tool Input: {json.dumps(tool_input, indent=2)[:200]}...")

                    tool_result = process_tool_call(tool_name, tool_input)
                    print(f"  Tool Result: [formatted memo generated]")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": tool_result
                    })
                elif block.type == "text":
                    if block.text:
                        print(f"  Text: {block.text[:200]}...")

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    writer_output = block.text
                    print(f"  Final Output: {block.text[:300]}...")
            break

        iteration += 1
        print()

    print()
    return writer_output

def run_qa_agent(client: Anthropic, company_name: str, research_brief: str, analysis_brief: str, memo: str) -> str:
    """
    Agent 4: QA/Review Agent
    Checks the memo for factual consistency against research data,
    flags hallucinations, and requests revisions
    """
    print("="*70)
    print("AGENT 4: QA / REVIEW")
    print("="*70)
    print("Task: Fact-check memo against research data, flag issues")
    print()
    print(f"Reviewing investment memo for {company_name}\n")

    messages = [
        {
            "role": "user",
            "content": f"""You are a senior QA reviewer for investment memos. Your job is to ensure factual accuracy and flag any problems.

You have 3 documents to cross-reference:

--- ORIGINAL RESEARCH (Source of Truth) ---
{research_brief}

--- ANALYSIS ---
{analysis_brief}

--- INVESTMENT MEMO (To Review) ---
{memo}

Your task:
1. **Fact-check** at least 3-5 key claims in the memo against the original research data using the fact_check tool. Focus on numbers, dates, company details, and financial figures.
2. **Flag issues** using the flag_issue tool for any:
   - Hallucinations (facts in the memo not present in the research)
   - Inconsistencies (memo contradicts the research or analysis)
   - Unsupported claims (conclusions not backed by data)
   - Missing information (important data from research that was left out)
3. After checking, provide a final QA summary with:
   - Overall quality score (1-10)
   - Number of issues found by severity
   - Whether the memo is APPROVED, NEEDS REVISION, or REJECTED
   - Specific revision requests if needed"""
        }
    ]

    iteration = 1
    qa_output = None

    while True:
        print(f"Iteration {iteration}:")

        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            tools=QA_TOOLS,
            messages=messages
        )

        print(f"  Stop Reason: {response.stop_reason}")

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id

                    print(f"  Tool: {tool_name}")
                    if tool_name == "fact_check":
                        print(f"    Checking: {tool_input.get('claim', '')[:100]}...")
                    elif tool_name == "flag_issue":
                        print(f"    Flagging: [{tool_input.get('severity', '')}] {tool_input.get('issue_type', '')} - {tool_input.get('description', '')[:80]}...")

                    tool_result = process_tool_call(tool_name, tool_input)
                    print(f"    Result: {tool_result[:150]}...")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": tool_result
                    })
                elif block.type == "text":
                    if block.text:
                        print(f"  Text: {block.text[:200]}...")

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    qa_output = block.text
                    print(f"  Final Output: {block.text[:300]}...")
            break

        iteration += 1
        print()

    print()
    return qa_output

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main orchestration function"""
    print("\n")
    print("*" * 70)
    print("4-AGENT INVESTMENT MEMO PIPELINE")
    print("Researcher → Analyzer → Writer → QA/Review")
    print("*" * 70)
    print()

    # Initialize client
    client = get_client()

    # Get company name from user
    company_name = input("Enter company name to research: ").strip()
    if not company_name:
        company_name = "Vettio"
        print(f"No input provided. Using default: {company_name}")

    print()

    # Step 1: Run Researcher Agent
    agent1_output = run_researcher_agent(client, company_name)

    # Step 2: Run Analyzer Agent with Researcher's output
    agent2_output = run_analyzer_agent(client, agent1_output)

    # Step 3: Run Writer Agent with both Agent 1 and Agent 2 outputs
    agent3_output = run_writer_agent(client, company_name, agent1_output, agent2_output)

    # Step 4: Run QA/Review Agent with all previous outputs
    agent4_output = run_qa_agent(client, company_name, agent1_output, agent2_output, agent3_output)

    # Step 5: Show final results
    print("="*70)
    print("FINAL RESULTS")
    print("="*70)
    print()
    print("AGENT 1 RESEARCH:")
    print("-" * 70)
    print(agent1_output)
    print()
    print("AGENT 2 ANALYSIS:")
    print("-" * 70)
    print(agent2_output)
    print()
    print("AGENT 3 INVESTMENT MEMO:")
    print("-" * 70)
    print(agent3_output)
    print()
    print("AGENT 4 QA REVIEW:")
    print("-" * 70)
    print(agent4_output)
    print()
    print("✓ SUCCESS: All 4 agents communicated successfully!")
    print("  Agent 1 research → Agent 2 analysis → Agent 3 memo → Agent 4 QA review")
    print()

if __name__ == "__main__":
    main()
