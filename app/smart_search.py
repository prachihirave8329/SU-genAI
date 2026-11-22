
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize_text(text):
    """Normalize text for consistent medicine matching."""
    return re.sub(r"\s+", " ", str(text).lower()).strip()


def search_records(query, records):
    """Search medicines using weighted name, strength and TF-IDF matching."""

    if not query or not query.strip() or not records:
        return []

    normalized_query = normalize_text(query)
    query_tokens = set(normalized_query.split())

    documents = []

    for record in records:
        text = (
            f"{record['generic_name']} "
            f"{record['strength']} "
            f"{record['unit_size']} "
            f"{record['therapeutic_group']}"
        )
        documents.append(text)

    vectorizer = TfidfVectorizer()
    medicine_vectors = vectorizer.fit_transform(documents)
    query_vector = vectorizer.transform([normalized_query])

    scores = cosine_similarity(
        query_vector,
        medicine_vectors
    ).flatten()

    results = []

    for index, record in enumerate(records):
        generic_name = normalize_text(record["generic_name"])
        strength = normalize_text(record["strength"])

        name_match = generic_name in normalized_query
        query_name_match = normalized_query.startswith(generic_name)

        name_tokens = set(generic_name.split())
        name_token_match = bool(name_tokens & query_tokens)

        strength_match = bool(
            set(strength.split()) & query_tokens
        )

        # Require a medicine-name match to avoid unrelated results.
        if not name_match and not name_token_match:
            continue

        similarity = float(scores[index])

        # Combine semantic similarity with exact matching signals.
        final_score = similarity

        if name_match:
            final_score += 1.0
        elif query_name_match or name_token_match:
            final_score += 0.5

        if strength_match:
            final_score += 0.25

        result = record.copy()
        result["similarity_score"] = round(final_score, 4)
        results.append(result)

    results.sort(
        key=lambda item: item["similarity_score"],
        reverse=True
    )

    return results
