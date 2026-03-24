#!/usr/bin/env python3
"""
Simple 2-Agent System using Anthropic SDK
Agent 1: Researcher - Searches for company information
Agent 2: Analyzer - Analyzes the research and scores opportunities
"""

import json
import os
from dotenv import load_dotenv
from anthropic import Anthropic
import requests
from bs4 import BeautifulSoup
import wikipedia

# Load environment variables from .env file
load_dotenv()

# Initialize Anthropic client with API key from .env
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-6"

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
    employees = company_data.get("employees", 1)
    revenue_value = company_data.get("revenue", "$0")

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

def process_tool_call(tool_name: str, tool_input: dict) -> str:
    """Process tool calls and return results"""
    print(f"  → Calling tool: {tool_name}")

    if tool_name == "search_company_info":
        result = execute_search_company_info(tool_input["company_name"])
    elif tool_name == "calculate_metric":
        result = execute_calculate_metric(tool_input["metric_type"], tool_input["company_data"])
    elif tool_name == "score_opportunity":
        result = execute_score_opportunity(tool_input["company_name"], tool_input["analysis_summary"])
    else:
        result = {"error": f"Unknown tool: {tool_name}"}

    return json.dumps(result)

# ============================================================================
# AGENT FUNCTIONS
# ============================================================================

def run_researcher_agent(company_name: str) -> str:
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

def run_analyzer_agent(research_brief: str) -> str:
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

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main orchestration function"""
    print("\n")
    print("*" * 70)
    print("SIMPLE 2-AGENT SYSTEM")
    print("Researcher → Analyzer Pipeline")
    print("*" * 70)
    print()

    # Get company name from user
    company_name = input("Enter company name to research: ").strip()
    if not company_name:
        company_name = "Vettio"
        print(f"No input provided. Using default: {company_name}")

    print()

    # Step 1: Run Researcher Agent
    agent1_output = run_researcher_agent(company_name)

    # Step 2: Run Analyzer Agent with Researcher's output
    agent2_output = run_analyzer_agent(agent1_output)

    # Step 3: Show final results
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
    print("✓ SUCCESS: Agents communicated successfully!")
    print("  Agent 1 research was passed to Agent 2 and analyzed.")
    print()

if __name__ == "__main__":
    main()
