import json
from pathlib import Path

from app.vectorstore import semantic_search

DATASET_PATH = Path("evaluation/retrieval_dataset.json")
TOP_K = 3


def evaluate_retrieval():
    with DATASET_PATH.open(encoding="utf-8") as file:
        dataset = json.load(file)

    reciprocal_ranks = []
    successful_queries = 0

    for item in dataset:
        query = item["query"]
        expected_source = item["expected_source"]
        expected_terms = [
            term.lower() for term in item["expected_terms"]
        ]

        results = semantic_search(query, n_results=TOP_K)

        relevant_rank = None

        for rank, (metadata, document) in enumerate(
            zip(
                results["metadatas"][0],
                results["documents"][0],
            ),
            start=1,
        ):
            document_lower = document.lower()

            source_matches = metadata["source"] == expected_source
            terms_match = all(
                term in document_lower for term in expected_terms
            )

            if source_matches and terms_match:
                relevant_rank = rank
                break

        if relevant_rank is not None:
            successful_queries += 1
            reciprocal_ranks.append(1 / relevant_rank)
        else:
            reciprocal_ranks.append(0)

        print(f"\nQuery: {query}")
        print(f"Expected source: {expected_source}")
        print(f"Relevant result rank: {relevant_rank}")

    hit_rate = successful_queries / len(dataset)
    mrr = sum(reciprocal_ranks) / len(dataset)

    print("\n========== RETRIEVAL EVALUATION ==========")
    print(f"Total queries: {len(dataset)}")
    print(f"Successful queries in Top {TOP_K}: {successful_queries}")
    print(f"Hit Rate@{TOP_K}: {hit_rate:.2%}")
    print(f"Mean Reciprocal Rank (MRR): {mrr:.4f}")


if __name__ == "__main__":
    evaluate_retrieval()