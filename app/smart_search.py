
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def search_records(query, records):
    # Handle empty input
    if not query or not query.strip():
        return []

    if not records:
        return []

    # Convert each medicine record into searchable text
    documents = []

    for record in records:
        text = (
            record["generic_name"] + " " +
            record["strength"] + " " +
            record["unit_size"] + " " +
            record["therapeutic_group"]
        )
        documents.append(text)

    # Convert medicine descriptions into TF-IDF vectors
    vectorizer = TfidfVectorizer()

    medicine_vectors = vectorizer.fit_transform(documents)

    # Convert the user's query into a vector
    query_vector = vectorizer.transform([query])

    # Calculate similarity scores
    scores = cosine_similarity(
        query_vector,
        medicine_vectors
    ).flatten()

    # Rank medicines from highest to lowest similarity
    results = []

    for index, score in enumerate(scores):
        if score > 0:
            result = records[index].copy()
            result["similarity_score"] = round(float(score), 4)
            results.append(result)

    results.sort(
        key=lambda item: item["similarity_score"],
        reverse=True
    )

    return results
