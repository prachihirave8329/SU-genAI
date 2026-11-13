
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Question asked by the user"
    )

    task: str = Field(
        default="medicine",
        description="Task type: medicine or general"
    )


class ChatResponse(BaseModel):
    answer: str

    confidence: float = Field(
        ge=0,
        le=1
    )

    follow_up: str
