
import json

from app.graph import execute_tool


def test_agent_tool_calculates_savings():
    state = {
        "drug_code": "SAMPLE001",
        "branded_price": 50,
        "branded_pack_size": 10,
        "tablets_per_day": 2
    }

    result = execute_tool(state)

    # Convert the tool's JSON result into a Python dictionary
    data = json.loads(result["result"])

    assert data["monthly_savings"] == 210.0
    assert data["yearly_savings"] == 2520.0


def test_agent_tool_missing_input():
    state = {
        "drug_code": "SAMPLE001"
    }

    result = execute_tool(state)

    assert result["result"] == "Missing input: branded_price"
