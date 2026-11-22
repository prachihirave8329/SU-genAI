
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

# Targeted query expansions for general scheme questions
QUERY_EXPANSIONS = {
    "what is jan aushadhi": (
        "What is Pradhan Mantri Bhartiya Janaushadhi "
        "Pariyojana (PMBJP) and what is its purpose?"
    ),
    "what is the objective of jan aushadhi": (
        "What is the objective and purpose of Pradhan "
        "Mantri Bhartiya Janaushadhi Pariyojana (PMBJP)?"
    ),
    "what is the purpose of jan aushadhi": (
        "What is Pradhan Mantri Bhartiya Janaushadhi "
        "Pariyojana (PMBJP) and what is its purpose?"
    ),
    "what is the purpose of pmbjp": (
        "What is Pradhan Mantri Bhartiya Janaushadhi "
        "Pariyojana (PMBJP)? It provides quality generic "
        "medicines at affordable prices."
    ),
    "how are medicines procured and quality tested": (
        "Medicines are procured through open tender from "
        "manufacturers. Each batch is tested at empanelled "
        "NABL accredited laboratories for quality."
    ),
}
def expand_query(query):
    """Expand common general questions using official scheme terminology."""

    normalized_query = " ".join(
        query.lower().strip(" ?.!").split()
    )

    return QUERY_EXPANSIONS.get(normalized_query, query)


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

    expanded_query = expand_query(query)

    results = collection.query(
        query_texts=[expanded_query],
        n_results=min(n_results, collection.count())
    )

    return results


if __name__ == "__main__":

    print("Testing query expansion...")

    test_queries = [
        "What is Jan Aushadhi?",
        "What is PMBJP?",
        "Find Paracetamol products"
    ]

    for query in test_queries:
        print("\nOriginal query:", query)
        print("Expanded query:", expand_query(query))

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
