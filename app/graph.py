
import json
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from app.agent_loop import rag_search
from app.llm import generate_response
from app.tools import monthly_savings_calculator


# 1. Define agent state
class AgentState(TypedDict, total=False):
    question: str
    task: str
    approved: bool
    drug_code: str
    branded_price: float
    branded_pack_size: int
    tablets_per_day: float
    selected_tool: str
    result: str
    answer: str
    history: list


# 2. Remember conversation
def remember(state: AgentState):

    history = state.get("history", [])

    history = history + [
        {"role": "user", "content": state["question"]}
    ]

    return {"history": history}


# 3. Decide which tool to use
def decide(state: AgentState):

    question = state["question"].lower()
    task = state.get("task", "")

    if task == "savings" or "save" in question or "savings" in question:
        tool = "calculator"
    else:
        tool = "rag"

    return {"selected_tool": tool}


# 4. Ask for approval
def approval(state: AgentState):

    decision = interrupt({
        "message": "Do you approve this action?",
        "tool": state["selected_tool"]
    })

    return {"approved": decision is True}


# 5. Execute calculator
def execute_tool(state: AgentState):

    required = [
        "drug_code",
        "branded_price",
        "branded_pack_size",
        "tablets_per_day"
    ]

    for field in required:
        if field not in state:
            return {"result": f"Missing input: {field}"}

    result = monthly_savings_calculator(
        state["drug_code"],
        state["branded_price"],
        state["branded_pack_size"],
        state["tablets_per_day"]
    )

    return {"result": json.dumps(result)}


# 6. Execute RAG
def execute_rag(state: AgentState):

    result = rag_search(state["question"])

    return {"result": json.dumps(result, ensure_ascii=False)}


# 7. Generate final answer
def answer(state: AgentState):

    system_prompt = """
    You are a helpful Jan Aushadhi assistant.
    Answer using only the tool result.
    Use simple language.
    Do not invent information.
    Clearly explain monthly and yearly savings when available.
    Do not recommend changing medicines or doses.
    Return JSON:
    {"answer": "your answer"}
    """

    user_prompt = f"""
    Conversation history:
    {json.dumps(state.get("history", []), ensure_ascii=False)}

    User question:
    {state["question"]}

    Tool result:
    {state.get("result", "")}
    """

    response = generate_response(system_prompt, user_prompt)
    result = json.loads(response)

    final_answer = result["answer"]

    history = state.get("history", [])
    history = history + [
        {"role": "assistant", "content": final_answer}
    ]

    return {
        "answer": final_answer,
        "history": history
    }


# 8. Handle rejected approval
def rejected(state: AgentState):

    message = "Action was not approved."

    history = state.get("history", [])
    history = history + [
        {"role": "assistant", "content": message}
    ]

    return {
        "answer": message,
        "history": history
    }


# 9. Select next action
def select_action(state: AgentState):

    if not state.get("approved", False):
        return "rejected"

    if state["selected_tool"] == "calculator":
        return "tool"

    return "rag"


# 10. Build graph
builder = StateGraph(AgentState)

builder.add_node("remember", remember)
builder.add_node("decide", decide)
builder.add_node("approval", approval)
builder.add_node("tool", execute_tool)
builder.add_node("rag", execute_rag)
builder.add_node("answer", answer)
builder.add_node("rejected", rejected)

builder.add_edge(START, "remember")
builder.add_edge("remember", "decide")
builder.add_edge("decide", "approval")

builder.add_conditional_edges(
    "approval",
    select_action,
    {
        "tool": "tool",
        "rag": "rag",
        "rejected": "rejected"
    }
)

builder.add_edge("tool", "answer")
builder.add_edge("rag", "answer")
builder.add_edge("answer", END)
builder.add_edge("rejected", END)


# 11. Add memory and compile
memory = InMemorySaver()

agent = builder.compile(checkpointer=memory)
