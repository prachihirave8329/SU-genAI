
import gc
from pathlib import Path

import chromadb

from app.chunking import chunk_documents

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# ChromaDB database location
DB_DIR = BASE_DIR / "data" / "chroma_db"

# Existing production collection
COLLECTION_NAME = "jan_aushadhi_docs"

# Small batch size for low-memory deployment
BATCH_SIZE = 16


def get_client():
    """Create a persistent ChromaDB client."""
    return chromadb.PersistentClient(path=str(DB_DIR))


def get_collection(collection_name=COLLECTION_NAME):
    """Get or create a ChromaDB collection."""

    client = get_client()

    embedding_function = (
        chromadb.utils.embedding_functions.DefaultEmbeddingFunction()
    )

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_function
    )

    return collection


def index_chunks(
    chunk_size=500,
    overlap=50,
    collection_name=COLLECTION_NAME
):
    """Store document chunks in small batches to reduce memory usage."""

    chunks = chunk_documents(
        chunk_size=chunk_size,
        overlap=overlap
    )

    collection = get_collection(collection_name)

    total_chunks = len(chunks)

    print(f"Starting indexing of {total_chunks} chunks...")
    print(f"Batch size: {BATCH_SIZE}")

    for start in range(0, total_chunks, BATCH_SIZE):

        batch = chunks[start:start + BATCH_SIZE]

        ids = [
            f"chunk_{i}"
            for i in range(start, start + len(batch))
        ]

        documents = [
            chunk["text"]
            for chunk in batch
        ]

        metadatas = [
            {
                "source": chunk["source"],
                "page": chunk["page"],
                "title": chunk["title"]
            }
            for chunk in batch
        ]

        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

        print(
            f"Indexed "
            f"{min(start + len(batch), total_chunks)}"
            f"/{total_chunks} chunks"
        )

        # Release temporary batch data
        del batch
        del ids
        del documents
        del metadatas

        gc.collect()

    del chunks
    gc.collect()

    print("Indexing completed!")
    print("Collection:", collection_name)
    print("Total chunks indexed:", collection.count())

    return collection


def semantic_search(
    query,
    n_results=5,
    collection_name=COLLECTION_NAME
):
    """Search indexed documents using semantic similarity."""

    collection = get_collection(collection_name)

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    return results


if __name__ == "__main__":

    index_chunks()

    print("\nTesting semantic search...")

    results = semantic_search(
        "What is the objective of Jan Aushadhi?"
    )

    for i, document in enumerate(
        results["documents"][0],
        start=1
    ):

        metadata = results["metadatas"][0][i - 1]

        print(f"\nResult {i}")
        print("Source:", metadata["source"])
        print("Page:", metadata["page"])
        print("Title:", metadata["title"])
        print("Text:", document[:300])
