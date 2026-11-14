
import chromadb
from pathlib import Path

from app.chunking import chunk_documents


BASE_DIR = Path(__file__).resolve().parent.parent
EVAL_DIR = BASE_DIR / "eval"


QUESTIONS = [
    "What is Pradhan Mantri Bhartiya Janaushadhi Pariyojana?",
    "What is the main objective of PMBI?",
    "How do Jan Aushadhi Kendras help ordinary people?",
    "Where can I find a nearby Jan Aushadhi Kendra?",
    "What are generic medicines?",
    "How are the quality of medicines ensured?",
    "Who manages the Jan Aushadhi scheme?",
    "How can someone open a Jan Aushadhi Kendra?",
    "How can customers get information about medicines?",
    "What is the toll-free contact number for Jan Aushadhi?"
]


def create_embedding_function():
    return chromadb.utils.embedding_functions.DefaultEmbeddingFunction()


def embed_texts(texts):
    embedding_function = create_embedding_function()
    return embedding_function(texts)


def run_evaluation():

    # Load chunks from source documents
    chunks = chunk_documents()

    print("Total chunks:", len(chunks))

    # Create temporary ChromaDB client
    client = chromadb.EphemeralClient()

    embedding_function = create_embedding_function()

    collection = client.create_collection(
        name="jan_aushadhi_evaluation",
        embedding_function=embedding_function
    )

    # Prepare data for ChromaDB
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    documents = [chunk["text"] for chunk in chunks]

    metadatas = [
        {
            "source": chunk["source"],
            "page": chunk["page"],
            "title": chunk["title"]
        }
        for chunk in chunks
    ]

    # Store chunks and their embeddings
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print("Chunks indexed:", collection.count())

    # Search using all 10 questions
    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    output_file = EVAL_DIR / "search_results.md"

    with open(output_file, "w", encoding="utf-8") as file:

        file.write("# JanAushadhiFinder Semantic Search Evaluation\n\n")
        file.write(f"Total indexed chunks: {collection.count()}\n\n")

        for index, question in enumerate(QUESTIONS, start=1):

            results = collection.query(
                query_texts=[question],
                n_results=3
            )

            file.write(f"## Question {index}: {question}\n\n")

            for i in range(len(results["ids"][0])):

                file.write(f"### Result {i + 1}\n\n")

                metadata = results["metadatas"][0][i]

                file.write(f"- Source: {metadata['source']}\n")
                file.write(f"- Page: {metadata['page']}\n")
                file.write(f"- Title: {metadata['title']}\n")
                file.write(
                    f"- Distance: {results['distances'][0][i]:.4f}\n\n"
                )

                file.write(
                    results["documents"][0][i][:500] + "\n\n"
                )

            file.write("---\n\n")

    print("Evaluation completed!")
    print("Results saved to:", output_file)


if __name__ == "__main__":
    run_evaluation()
