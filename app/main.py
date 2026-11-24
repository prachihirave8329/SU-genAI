
import asyncio
import json
import logging
import time
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


# --------------------------------------------------
# Document indexing - background initialization
# --------------------------------------------------

def initialize_vectorstore_sync():
    """Initialize ChromaDB and index documents if necessary."""

    collection = get_collection()

    existing_count = collection.count()

    logger.info(
        "Existing ChromaDB chunks: %s",
        existing_count,
    )

    if existing_count == 0:
        logger.info("Starting background document indexing...")

        collection = index_chunks()

    total_chunks = collection.count()

    if total_chunks == 0:
        raise RuntimeError(
            "Document indexing completed without creating chunks."
        )

    logger.info(
        "Document indexing completed successfully. "
        "Total chunks: %s",
        total_chunks,
    )

    return total_chunks


async def initialize_vectorstore(app: FastAPI):
    """Run document indexing without blocking API startup."""

    app.state.indexing_status = "indexing"

    try:
        total_chunks = await asyncio.to_thread(
            initialize_vectorstore_sync
        )

        app.state.indexing_status = "ready"

        logger.info(
            "Document indexing status: ready (%s chunks)",
            total_chunks,
        )

    except Exception:
        app.state.indexing_status = "failed"

        logger.exception(
            "Background document indexing failed."
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Start the API immediately.

    Document indexing runs in a background task so that
    Render can detect the API port without waiting for
    ChromaDB initialization to finish.
    """

    app.state.indexing_status = "starting"

    app.state.indexing_task = asyncio.create_task(
        initialize_vectorstore(app)
    )

    logger.info(
        "API startup complete. Document indexing is running "
        "in the background."
    )

    yield


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="JanAushadhiFinder API",
    description="API for exploring and searching Jan Aushadhi medicines.",
    version="2.0.0",
    lifespan=lifespan,
)
@app.middleware("http")
async def log_api_latency(request, call_next):

    start_time = time.perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response

    finally:
        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.info(
            "api_request method=%s path=%s "
            "status_code=%s latency_ms=%.2f",
            request.method,
            request.url.path,
            status_code,
            latency_ms,
        )

app.include_router(agent_router)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "records.json"


# --------------------------------------------------
# Medicine records
# --------------------------------------------------

def load_records():
    """Load medicine records from the JSON dataset."""

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


@app.get("/")
def home():
    return {
        "message": "Welcome to JanAushadhiFinder API!",
        "docs": "/docs",
        "health": "/health",
    }


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/health")
def health_check():
    """Check API health and document indexing status."""

    return {
        "status": "healthy",
        "message": "JanAushadhiFinder API is running!",
        "document_index_status": getattr(
            app.state,
            "indexing_status",
            "starting",
        ),
    }


# --------------------------------------------------
# Medicine record endpoints
# --------------------------------------------------

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


# --------------------------------------------------
# Medicine search
# --------------------------------------------------

@app.get("/search")
def search_medicines(q: str = Query(..., min_length=1)):
    records = load_records()
    results = search_records(q, records)

    return {
        "query": q,
        "total_results": len(results),
        "results": results,
    }


# --------------------------------------------------
# Semantic document search
# --------------------------------------------------

@app.get("/search/semantic")
def semantic_search_api(q: str = Query(..., min_length=1)):

    # Do not search ChromaDB before indexing is complete.
    indexing_status = getattr(
        app.state,
        "indexing_status",
        "starting",
    )

    if indexing_status != "ready":
        raise HTTPException(
            status_code=503,
            detail=(
                "Document indexing is not ready. "
                "Please retry later."
            ),
        )

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

    except HTTPException:
        raise

    except Exception as error:
        logger.exception("SEMANTIC SEARCH ERROR")

        raise HTTPException(
            status_code=500,
            detail=(
                "Semantic search failed: "
                f"{type(error).__name__}: {error}"
            ),
        ) from error


# --------------------------------------------------
# Question-based medicine search
# --------------------------------------------------

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


# --------------------------------------------------
# Chat endpoint
# --------------------------------------------------

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

    except Exception:
        logger.exception("LLM ERROR")

        raise HTTPException(
            status_code=502,
            detail="LLM provider request failed. Check server terminal.",
        )


# --------------------------------------------------
# RAG endpoint
# --------------------------------------------------

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

    except Exception:
        logger.exception("RAG ERROR")

        raise HTTPException(
            status_code=502,
            detail="RAG question processing failed.",
        )
