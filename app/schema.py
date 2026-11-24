
from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000
    )

    task: str = Field(
        default="medicine"
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Question cannot be empty.")

        return value

    @field_validator("task")
    @classmethod
    def validate_task(cls, value):
        if value not in ("medicine", "general"):
            raise ValueError(
                "Task must be medicine or general."
            )

        return value


class ChatResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)
    follow_up: str


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Question cannot be empty.")

        return value
