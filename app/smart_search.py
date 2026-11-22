import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

NAME_STOP_WORDS = {
    "mg", "mcg", "ug", "gm", "kg", "ml", "iu", "units", "unit",
    "tablet", "tablets", "capsule", "capsules", "injection",
    "injections", "syrup", "suspension", "solution", "cream",
    "ointment", "gel", "drops", "powder", "granules",
    "ip", "bp", "usp", "and", "with", "for", "the",
    "what", "is", "are", "of", "a", "an", "find", "search",
    "show", "list", "medicine", "medicines", "product", "products",
    "available", "prolonged", "release", "extended", "delayed",
    "sustained", "enteric", "coated", "dispersible",
}


def normalize_text(text):
    """Normalize text for consistent medicine matching."""
    return re.sub(r"\s+", " ", str(text).lower()).strip()


def medicine_name_tokens(text):
    """Extract meaningful medicine-name words, excluding dosage terms."""
    words = re.findall(r"[a-z]+", normalize_text(text))

    return {
        word
        for word in words
        if word not in NAME_STOP_WORDS and len(word) > 1
    }


def search_records(query, records):
    """Search medicines using ingredient matching and strength ranking."""

    if not query or not query.strip() or not records:
        return []

    normalized_query = normalize_text(query)

    query_name_tokens = medicine_name_tokens(normalized_query)

    # A dosage-only query should not return arbitrary medicines.
    if not query_name_tokens:
        return []

    query_strengths = set(
        re.findall(r"\d+(?:\.\d+)?", normalized_query)
    )

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
        medicine_tokens = medicine_name_tokens(
            record["generic_name"]
        )

        matching_tokens = query_name_tokens & medicine_tokens

        # Require at least one meaningful ingredient match.
        if not matching_tokens:
            continue

        record_strengths = set(
            re.findall(
                r"\d+(?:\.\d+)?",
                normalize_text(record["strength"])
            )
        )

        strength_match = bool(
            query_strengths & record_strengths
        )

        similarity = float(scores[index])

        # Reward meaningful ingredient matches.
        name_coverage = (
            len(matching_tokens) / len(query_name_tokens)
        )

        final_score = similarity + name_coverage

        # Give an additional bonus when all query-name tokens match.
        if query_name_tokens.issubset(medicine_tokens):
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
