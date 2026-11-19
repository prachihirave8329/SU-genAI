
import json

from app.llm import generate_response
from app.vectorstore import semantic_search

SYSTEM_PROMPT = """
You are JanAushadhiFinder, an evidence-grounded assistant.

Answer questions using ONLY the supplied retrieved document context.

Rules:
1. Never invent facts, medicine details, prices, or availability.
2. If the context does not contain sufficient evidence,
   answer exactly: "I don't know."
3. Do not assume that a medicine listed in the catalogue
   is currently in stock at a Kendra.
4. Do not provide diagnoses or prescribe medicines.
5. Keep answers simple and clear.
6. Select only the chunk IDs that directly support your answer.
7. Never invent or modify a chunk ID.
8. If the answer is "I don't know.", return an empty supporting_chunk_ids list.

Return ONLY valid JSON in this format:

{
    "answer": "Your answer",
    "supporting_chunk_ids": ["chunk_1"]
}

If evidence is insufficient, return:

{
    "answer": "I don't know.",
    "supporting_chunk_ids": []
}
"""


def ask_question(
    question: str,
    top_k: int = 5,
    collection_name: str = "jan_aushadhi_docs"
):

    question_lower = question.lower()

    # Do not claim live stock availability.
    stock_keywords = [
        "in stock",
        "stock availability",
        "stock at",
        "inventory",
        "currently available",
        "available right now"
    ]

    if any(keyword in question_lower for keyword in stock_keywords):
        return {
            "question": question,
            "answer": "I don't know.",
            "citations": [],
            "retrieved_chunks": []
        }

    # Step 1: Retrieve relevant chunks.
    results = semantic_search(
    query=question,
    n_results=top_k,
    collection_name=collection_name
)

    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    if not documents:
        return {
            "question": question,
            "answer": "I don't know.",
            "citations": [],
            "retrieved_chunks": []
        }

    # Step 2: Prepare context and metadata.
    context_parts = []
    retrieved_chunks = []

    for chunk_id, document, metadata in zip(ids, documents, metadatas):

        source = metadata.get("source", "Unknown")
        page = metadata.get("page", "Unknown")
        title = metadata.get("title", "Unknown")

        context_parts.append(
            f"""
Chunk ID: {chunk_id}
Source: {source}
Page: {page}
Title: {title}
Content: {document}
"""
        )

        retrieved_chunks.append({
            "chunk_id": chunk_id,
            "source": source,
            "page": page,
            "title": title,
            "text": document
        })

    context = "\n".join(context_parts)

    # Step 3: Prepare the LLM prompt.
    user_prompt = f"""
Retrieved document context:

{context}

User question:
{question}

Answer using only the retrieved evidence.

Return the IDs of only the chunks that directly support
your answer in supporting_chunk_ids.

If the evidence is insufficient, answer "I don't know."
and return an empty supporting_chunk_ids list.
"""

    # Step 4: Generate the answer.
    raw_response = generate_response(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt
    )

    try:
        parsed_response = json.loads(raw_response)
    except json.JSONDecodeError:
        raise ValueError("LLM returned invalid JSON.")

    if not isinstance(parsed_response, dict):
        raise TypeError("LLM response must be a JSON object.")
    answer = parsed_response.get("answer")
    supporting_ids = parsed_response.get("supporting_chunk_ids")

    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("LLM returned an invalid answer.")

    if not isinstance(supporting_ids, list):
        raise TypeError("Invalid supporting_chunk_ids returned by LLM.")
    # Step 5: Validate the LLM-selected chunk IDs.
    retrieved_by_id = {
        chunk["chunk_id"]: chunk
        for chunk in retrieved_chunks
    }

    valid_ids = [
        chunk_id
        for chunk_id in supporting_ids
        if isinstance(chunk_id, str) and chunk_id in retrieved_by_id
    ]

    # Step 6: Return citations only when evidence is selected.
    if answer.strip().lower() == "i don't know." or not valid_ids:
        answer = "I don't know."
        citations = []
    else:
        citations = [
            {
                "chunk_id": retrieved_by_id[chunk_id]["chunk_id"],
                "source": retrieved_by_id[chunk_id]["source"],
                "page": retrieved_by_id[chunk_id]["page"],
                "title": retrieved_by_id[chunk_id]["title"]
            }
            for chunk_id in dict.fromkeys(valid_ids)
        ]

    return {
        "question": question,
        "answer": answer.strip(),
        "citations": citations,
        "retrieved_chunks": retrieved_chunks
    }
