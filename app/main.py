
import json
from pathlib import Path

from fastapi import FastAPI, Query, HTTPException

from app.smart_search import search_records
from app.schema import ChatRequest, ChatResponse
from app.services import generate_chat_answer


app = FastAPI(
    title="JanAushadhiFinder API",
    description="API for exploring and searching Jan Aushadhi medicines.",
    version="2.0.0"
)


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "records.json"


def load_records():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


@app.get("/")
def home():
    return {
        "message": "Welcome to JanAushadhiFinder API!",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "JanAushadhiFinder API is running!"
    }


@app.get("/records")
def get_records(limit: int | None = Query(default=None, ge=1)):
    records = load_records()

    if limit is not None:
        records = records[:limit]

    return records


@app.get("/records/{id}")
def get_record_by_id(id: str):
    records = load_records()

    for record in records:
        if record["drug_code"] == id:
            return record

    raise HTTPException(
        status_code=404,
        detail="Medicine record not found"
    )


@app.get("/search")
def search_medicines(q: str = Query(..., min_length=1)):
    records = load_records()
    results = search_records(q, records)

    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }


@app.post("/questions")
def ask_question(request: ChatRequest):
    question = request.question
    records = load_records()
    results = search_records(question, records)

    return {
        "question": question,
        "total_results": len(results),
        "matching_records": results[:3],
        "message": (
            "Matching records found."
            if results
            else "No matching records found."
        ),
        "disclaimer": "This is a dataset search, not medical advice."
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    try:
        records = load_records()

        # Retrieve relevant records only for medicine queries
        if request.task == "medicine":
            matching_records = search_records(
                request.question,
                records
            )

            context_records = matching_records[:3]

        elif request.task == "general":
            context_records = []

        else:
            raise HTTPException(
                status_code=400,
                detail="Task must be medicine or general"
            )

        result = generate_chat_answer(
            question=request.question,
            records=context_records,
            task=request.task
        )

        return result

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error)
        )

    except Exception as error:
            print(
        f"LLM ERROR: {type(error).__name__}: {error}"
    )

    raise HTTPException(
        status_code=502,
        detail="LLM provider request failed. Check server terminal."
    )
