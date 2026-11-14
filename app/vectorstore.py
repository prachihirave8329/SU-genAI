
from pathlib import Path
import chromadb

from app.chunking import chunk_documents


# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# ChromaDB database location
DB_DIR = BASE_DIR / "data" / "chroma_db"

COLLECTION_NAME = "jan_aushadhi_docs"


def get_client():
    """Create a persistent ChromaDB client."""

    return chromadb.PersistentClient(
        path=str(DB_DIR)
    )


def get_collection():
    """Get or create the medicine documents collection."""

    client = get_client()

    embedding_function = (
        chromadb.utils.embedding_functions.DefaultEmbeddingFunction()
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function
    )

    return collection


def index_chunks():
    """Store all document chunks in ChromaDB."""

    chunks = chunk_documents()

    collection = get_collection()

    ids = [
        f"chunk_{i}"
        for i in range(len(chunks))
    ]

    documents = [
        chunk["text"]
        for chunk in chunks
    ]

    metadatas = [
        {
            "source": chunk["source"],
            "page": chunk["page"],
            "title": chunk["title"]
        }
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print("Indexing completed!")
    print("Total chunks indexed:", collection.count())

    return collection


def semantic_search(query, n_results=3):

    collection = get_collection()

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

    for i, document in enumerate(results["documents"][0], start=1):

        metadata = results["metadatas"][0][i - 1]

        print(f"\nResult {i}")
        print("Source:", metadata["source"])
        print("Page:", metadata["page"])
        print("Title:", metadata["title"])
        print("Text:", document[:300])
