
import json
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

from app.vectorstore import semantic_search
from app.llm import generate_response


# 1. Define the graph state
class AgentState(TypedDict, total=False):
    question: str
    history: list
    documents: list
    answer: str
    approved: bool


# 2. Remember the conversation
def remember_node(state: AgentState):

    history = state.get("history", [])

    history = history + [
        {
            "role": "user",
            "content": state["question"]
        }
    ]

    return {"history": history}


# 3. Ask for human approval
def approval_node(state: AgentState):

    decision = interrupt({
        "message": "Do you approve the RAG search?",
        "question": state["question"]
    })

    return {"approved": decision is True}


# 4. Execute RAG search
def search_node(state: AgentState):

    results = semantic_search(
        state["question"],
        n_results=5
    )

    documents = results["documents"][0]

    return {"documents": documents}


# 5. Generate the final answer
def answer_node(state: AgentState):

    system_prompt = """
    You are a helpful Jan Aushadhi assistant.

    Answer using only the retrieved documents.
    Use simple language.
    Use conversation history to understand follow-up questions.
    Do not invent information.
    If the documents do not contain the answer, say so.

    Return JSON:
    {"answer": "your answer"}
    """

    user_prompt = f"""
    Conversation history:
    {json.dumps(state.get("history", []), ensure_ascii=False)}

    Retrieved documents:
    {json.dumps(state.get("documents", []), ensure_ascii=False)}

    Current question:
    {state["question"]}
    """

    response = generate_response(
        system_prompt,
        user_prompt
    )

    result = json.loads(response)

    answer = result["answer"]

    history = state.get("history", [])

    history = history + [
        {
            "role": "assistant",
            "content": answer
        }
    ]

    return {
        "answer": answer,
        "history": history
    }


# 6. Handle rejected approval
def rejected_node(state: AgentState):

    answer = "Search was not approved."

    history = state.get("history", [])

    history = history + [
        {
            "role": "assistant",
            "content": answer
        }
    ]

    return {
        "answer": answer,
        "history": history
    }


# 7. Decide the next node
def approval_router(state: AgentState):

    if state["approved"]:
        return "search"

    return "rejected"


# 8. Build the graph
builder = StateGraph(AgentState)

builder.add_node("remember", remember_node)
builder.add_node("approval", approval_node)
builder.add_node("search", search_node)
builder.add_node("answer", answer_node)
builder.add_node("rejected", rejected_node)

builder.add_edge(START, "remember")
builder.add_edge("remember", "approval")

builder.add_conditional_edges(
    "approval",
    approval_router,
    {
        "search": "search",
        "rejected": "rejected"
    }
)

builder.add_edge("search", "answer")
builder.add_edge("answer", END)
builder.add_edge("rejected", END)


# 9. Add memory and compile
memory = InMemorySaver()

agent = builder.compile(
    checkpointer=memory
)


# 10. Run the agent
if __name__ == "__main__":

    config = {
        "configurable": {
            "thread_id": "jan-aushadhi-session-1"
        }
    }

    print("LangGraph Agent Started!")

    while True:

        question = input("\nYou: ")

        if question.lower() == "exit":
            print("Agent stopped!")
            break

        try:

            result = agent.invoke(
                {"question": question},
                config
            )

            # Check whether approval is required
            if "__interrupt__" in result:

                print("\nApproval required:")
                print(result["__interrupt__"][0].value)

                decision = input("Approve? (yes/no): ")

                approved = decision.lower() == "yes"

                result = agent.invoke(
                    Command(resume=approved),
                    config
                )

            print("\nAgent:", result["answer"])

        except Exception as error:

            print("\nError:", error)
