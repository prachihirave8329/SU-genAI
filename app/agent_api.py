
from fastapi import FastAPI
from pydantic import BaseModel

from app.langgraph_agent import agent
from langgraph.types import Command

app = FastAPI(title="Jan Aushadhi Agent API")


class AgentInput(BaseModel):
    question: str
    thread_id: str = "jan-aushadhi-api"


class ApprovalInput(BaseModel):
    thread_id: str
    approved: bool


# Store pending approval information
pending_questions = {}


@app.get("/")
def home():
    return {"message": "Welcome to Jan Aushadhi Agent API"}


# Ask a question
@app.post("/agent")
def ask_agent(data: AgentInput):

    config = {
        "configurable": {
            "thread_id": data.thread_id
        }
    }

    result = agent.invoke(
        {"question": data.question},
        config
    )

    if "__interrupt__" in result:

        pending_questions[data.thread_id] = True

        return {
            "status": "approval_required",
            "message": result["__interrupt__"][0].value
        }

    return {
        "status": "completed",
        "answer": result["answer"]
    }


# Approve or reject a search
@app.post("/agent/approval")
def approve_agent(data: ApprovalInput):

    if data.thread_id not in pending_questions:
        return {"error": "No pending approval found"}

    config = {
        "configurable": {
            "thread_id": data.thread_id
        }
    }

    result = agent.invoke(
        Command(resume=data.approved),
        config
    )

    del pending_questions[data.thread_id]

    return {
        "status": "completed",
        "answer": result["answer"]
    }
