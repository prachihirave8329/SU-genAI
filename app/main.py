
import json
from pydantic import BaseModel, Field
from pathlib import Path
from fastapi import FastAPI, Query, HTTPException
from app.smart_search import search_records
app = FastAPI(
    title="JanAushadhiFinder API",
    description="API for exploring and searching Jan Aushadhi medicines.",
    version="1.0.0"
)
# Request model for user questions
class QuestionRequest(BaseModel):
    question: str = Field(min_length=1)
# Locate records.json
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "records.json"


# Load medicine records from JSON
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


# Health Check API
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "JanAushadhiFinder API is running!"
    }


# Get all medicine records or limit the results
@app.get("/records")
def get_records(limit: int | None = Query(default=None, ge=1)):
    records = load_records()

    if limit is not None:
        records = records[:limit]

    return records

# Get a medicine by drug code
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
# Search medicines using TF-IDF and cosine similarity
@app.get("/search")
def search_medicines(q: str = Query(..., min_length=1)):
    records = load_records()

    results = search_records(q, records)

    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }
# Ask questions about medicine records
@app.post("/questions")
def ask_question(request: QuestionRequest):

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