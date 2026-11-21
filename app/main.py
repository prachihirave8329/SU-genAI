
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

from app.agent_api import router as agent_router
from app.rag import ask_question as rag_ask_question
from app.schema import AskRequest, ChatRequest, ChatResponse
from app.services import generate_chat_answer
from app.smart_search import search_records
from app.vectorstore import (
    get_collection,
    index_chunks,
    semantic_search,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(logging.StreamHandler())

logger.propagate = False

# Initialize ChromaDB when the API starts

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.chunking import RAW_DIR, chunk_documents, load_documents

    logger.info("========== DOCUMENT INDEXING DIAGNOSTICS ==========")
    logger.info("Raw data directory: %s", RAW_DIR)
    logger.info("Raw directory exists: %s", RAW_DIR.exists())
    logger.info("Raw files: %s", list(RAW_DIR.glob("*")))

    documents = load_documents()
    logger.info("Documents loaded: %s", len(documents))

    chunks = chunk_documents()
    logger.info("Chunks generated: %s", len(chunks))

    collection = get_collection()
    logger.info("Existing ChromaDB chunks: %s", collection.count())

    if collection.count() == 0:
        logger.info("Starting document indexing...")
        index_chunks()
        logger.info("Indexed chunks: %s", collection.count())
    else:
        logger.info("ChromaDB already contains %s chunks.", collection.count())

    logger.info("========== INDEXING DIAGNOSTICS COMPLETE ==========")

    yield



app = FastAPI(
    title="JanAushadhiFinder API",
    description="API for exploring and searching Jan Aushadhi medicines.",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(agent_router)

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
        "health": "/health",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "JanAushadhiFinder API is running!",
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
        detail="Medicine record not found",
    )


@app.get("/search")
def search_medicines(q: str = Query(..., min_length=1)):
    records = load_records()
    results = search_records(q, records)

    return {
        "query": q,
        "total_results": len(results),
        "results": results,
    }


@app.get("/search/semantic")
def semantic_search_api(q: str = Query(..., min_length=1)):
    try:
        results = semantic_search(q, n_results=3)

        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        search_results = []

        for i in range(len(ids)):
            metadata = metadatas[i] or {}

            search_results.append({
                "id": ids[i],
                "text": documents[i],
                "source": metadata.get("source", "Unknown"),
                "page": metadata.get("page"),
                "title": metadata.get("title", "Untitled"),
                "distance": distances[i],
            })

        return {
            "query": q,
            "total_results": len(search_results),
            "results": search_results,
        }

    except Exception as error:
        logger.exception("SEMANTIC SEARCH ERROR")

        raise HTTPException(
            status_code=500,
            detail=(
                "Semantic search failed: "
                f"{type(error).__name__}: {error}"
            ),
        ) from error


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
        "disclaimer": "This is a dataset search, not medical advice.",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        records = load_records()

        if request.task == "medicine":
            matching_records = search_records(
                request.question,
                records,
            )
            context_records = matching_records[:3]

        elif request.task == "general":
            context_records = []

        else:
            raise HTTPException(
                status_code=400,
                detail="Task must be medicine or general",
            )

        result = generate_chat_answer(
            question=request.question,
            records=context_records,
            task=request.task,
        )

        return result

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception("LLM ERROR")

        raise HTTPException(
            status_code=502,
            detail="LLM provider request failed. Check server terminal.",
        ) from error


@app.post("/ask")
def ask_rag(request: AskRequest):
    try:
        result = rag_ask_question(
            request.question,
            top_k=5,
            collection_name="jan_aushadhi_config_b",
        )
        return result

    except ValueError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception("RAG ERROR")

        raise HTTPException(
            status_code=502,
            detail="RAG question processing failed.",
        ) from error
