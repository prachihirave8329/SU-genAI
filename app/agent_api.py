
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph.types import Command

from app.graph import agent


# Create FastAPI application
app = FastAPI(title="Jan Aushadhi Agent API")


# 1. User input model
class AgentInput(BaseModel):
    question: str
    thread_id: str = "jan-aushadhi-api"
    task: str = ""

    drug_code: str | None = None
    branded_price: float | None = None
    branded_pack_size: int | None = None
    tablets_per_day: float | None = None


# 2. Approval input model
class ApprovalInput(BaseModel):
    thread_id: str
    approved: bool


# Store pending approvals
pending_questions = set()


# 3. Home route
@app.get("/")
def home():
    return {
        "message": "Welcome to Jan Aushadhi Agent API"
    }


# 4. Run the LangGraph agent
@app.post("/agent")
def ask_agent(data: AgentInput):

    config = {
        "configurable": {
            "thread_id": data.thread_id
        }
    }

    # Prepare input for LangGraph
    state = data.model_dump(
        exclude={"thread_id"},
        exclude_none=True
    )

    try:
        result = agent.invoke(state, config)

        # Check whether human approval is required
        if "__interrupt__" in result:

            pending_questions.add(data.thread_id)

            return {
                "status": "approval_required",
                "thread_id": data.thread_id,
                "message": result["__interrupt__"][0].value
            }

        return {
            "status": "completed",
            "answer": result["answer"]
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# 5. Resume agent after approval
@app.post("/agent/approval")
def approve_agent(data: ApprovalInput):

    if data.thread_id not in pending_questions:
        raise HTTPException(
            status_code=404,
            detail="No pending approval found"
        )

    config = {
        "configurable": {
            "thread_id": data.thread_id
        }
    }

    try:
        result = agent.invoke(
            Command(resume=data.approved),
            config
        )

        pending_questions.remove(data.thread_id)

        return {
            "status": "completed",
            "approved": data.approved,
            "answer": result["answer"]
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
