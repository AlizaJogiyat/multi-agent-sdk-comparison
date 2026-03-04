"""MCP tool server for financial calculations."""

from claude_agent_sdk import tool, create_sdk_mcp_server

import json


@tool(
    "calculate",
    "Perform financial calculations. Supports: revenue_growth, profit_margin, debt_to_equity, current_ratio, roi, and custom expressions.",
    {"operation": str, "values": str},
)
async def calculate(args):
    """Perform a financial calculation.

    Args:
        operation: Type of calculation (revenue_growth, profit_margin, debt_to_equity,
                   current_ratio, roi, or expression)
        values: JSON string of numeric values, e.g. '{"current": 100, "previous": 80}'
    """
    operation = args["operation"]
    try:
        values = json.loads(args["values"])
    except json.JSONDecodeError:
        return {"content": [{"type": "text", "text": json.dumps({"error": "Invalid JSON in values"})}]}

    try:
        result = None

        if operation == "revenue_growth":
            current = float(values["current"])
            previous = float(values["previous"])
            if previous == 0:
                result = {"error": "Previous revenue is zero, cannot calculate growth"}
            else:
                growth = ((current - previous) / previous) * 100
                result = {"revenue_growth_pct": round(growth, 2)}

        elif operation == "profit_margin":
            revenue = float(values["revenue"])
            net_income = float(values["net_income"])
            if revenue == 0:
                result = {"error": "Revenue is zero"}
            else:
                margin = (net_income / revenue) * 100
                result = {"profit_margin_pct": round(margin, 2)}

        elif operation == "debt_to_equity":
            debt = float(values["total_debt"])
            equity = float(values["total_equity"])
            if equity == 0:
                result = {"error": "Total equity is zero"}
            else:
                ratio = debt / equity
                result = {"debt_to_equity_ratio": round(ratio, 2)}

        elif operation == "current_ratio":
            current_assets = float(values["current_assets"])
            current_liabilities = float(values["current_liabilities"])
            if current_liabilities == 0:
                result = {"error": "Current liabilities is zero"}
            else:
                ratio = current_assets / current_liabilities
                result = {"current_ratio": round(ratio, 2)}

        elif operation == "roi":
            gain = float(values["gain"])
            cost = float(values["cost"])
            if cost == 0:
                result = {"error": "Cost is zero"}
            else:
                roi = ((gain - cost) / cost) * 100
                result = {"roi_pct": round(roi, 2)}

        elif operation == "expression":
            expr = values.get("expr", "")
            allowed = set("0123456789+-*/.() ")
            if not all(c in allowed for c in expr):
                result = {"error": "Invalid characters in expression"}
            else:
                result = {"result": eval(expr)}  # noqa: S307 — restricted to digits/operators

        else:
            result = {"error": f"Unknown operation: {operation}"}

        return {"content": [{"type": "text", "text": json.dumps(result)}]}

    except (KeyError, ValueError) as e:
        return {"content": [{"type": "text", "text": json.dumps({"error": str(e)})}]}


def create_calculator_server():
    return create_sdk_mcp_server(
        name="calculator",
        version="1.0.0",
        tools=[calculate],
    )
