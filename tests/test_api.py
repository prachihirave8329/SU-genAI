
import json

from fastapi.testclient import TestClient

from app.main import app, load_records

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_records_endpoint():
    response = client.get("/records")

    assert response.status_code == 200
    assert len(response.json()) > 0


def test_search_endpoint():
    records = load_records()

    assert len(records) > 0

    # Use a medicine available in records.json
    query = records[0]["generic_name"]

    response = client.get(
        "/search",
        params={"q": query}
    )

    assert response.status_code == 200
    assert response.json()["total_results"] > 0


def test_ask_endpoint_with_fake_llm(monkeypatch):

    # Fake semantic search to avoid depending on ChromaDB
    def fake_semantic_search(query, n_results, collection_name):
        return {
            "ids": [["chunk_1"]],
            "documents": [
                ["Jan Aushadhi provides affordable generic medicines."]
            ],
            "metadatas": [
                [{"source": "test.pdf", "page": 1, "title": "Test"}]
            ]
        }

    # Fake LLM response to avoid calling an external AI API
    def fake_generate_response(system_prompt, user_prompt):
        return json.dumps({
            "answer": "Jan Aushadhi provides affordable generic medicines.",
            "supporting_chunk_ids": ["chunk_1"]
        })

    monkeypatch.setattr(
        "app.rag.semantic_search",
        fake_semantic_search
    )

    monkeypatch.setattr(
        "app.rag.generate_response",
        fake_generate_response
    )

    response = client.post(
        "/ask",
        json={"question": "What is Jan Aushadhi?"}
    )

    assert response.status_code == 200
    assert response.json()["answer"] == (
        "Jan Aushadhi provides affordable generic medicines."
    )
