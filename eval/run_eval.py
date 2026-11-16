
import json
from pathlib import Path

from app.rag import ask_question


BASE_DIR = Path(__file__).resolve().parent.parent
EVAL_FILE = BASE_DIR / "eval" / "eval_set.json"
RESULT_FILE = BASE_DIR / "eval" / "rag_eval_results.json"


CONFIGS = [
    {
        "name": "Config A",
        "collection_name": "jan_aushadhi_config_a",
        "top_k": 3
    },
    {
        "name": "Config B",
        "collection_name": "jan_aushadhi_config_b",
        "top_k": 5
    }
]


def evaluate_config(config, questions):
    results = []

    correct = 0
    abstention_correct = 0
    abstention_total = 0

    for item in questions:
        question_id = item["id"]
        question = item["question"]
        expected = item["expected_behavior"]

        print(f"\nTesting {question_id}: {question}")

        try:
            response = ask_question(
                question=question,
                top_k=config["top_k"],
                collection_name=config["collection_name"]
            )

            answer = response.get("answer", "")
            citations = response.get("citations", [])

            abstained = answer.strip().lower() == "i don't know."

            if expected == "abstain":
                is_correct = abstained
                abstention_total += 1

                if is_correct:
                    abstention_correct += 1
            else:
                is_correct = not abstained and len(citations) > 0

            if is_correct:
                correct += 1

            results.append({
                "id": question_id,
                "question": question,
                "expected_behavior": expected,
                "answer": answer,
                "citations": citations,
                "correct": is_correct
            })

            print("Answer:", answer)
            print("Citations:", len(citations))
            print("Correct:", is_correct)

        except Exception as error:
            print("Error:", str(error))

            results.append({
                "id": question_id,
                "question": question,
                "expected_behavior": expected,
                "answer": "",
                "citations": [],
                "correct": False,
                "error": str(error)
            })

    total = len(questions)
    accuracy = (correct / total * 100) if total else 0

    abstention_accuracy = (
        abstention_correct / abstention_total * 100
        if abstention_total else 0
    )

    return {
        "config": config["name"],
        "chunk_collection": config["collection_name"],
        "top_k": config["top_k"],
        "total_questions": total,
        "correct_answers": correct,
        "accuracy_percent": round(accuracy, 2),
        "abstention_accuracy_percent": round(abstention_accuracy, 2),
        "details": results
    }


def main():
    with open(EVAL_FILE, "r", encoding="utf-8") as file:
        questions = json.load(file)

    all_results = []

    for config in CONFIGS:
        print("\n" + "=" * 50)
        print("Evaluating:", config["name"])
        print("=" * 50)

        result = evaluate_config(config, questions)
        all_results.append(result)

    output = {
        "evaluation": "RAG Configuration Comparison",
        "results": all_results
    }

    with open(RESULT_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=4, ensure_ascii=False)

    print("\nEvaluation completed!")
    print("Results saved to:", RESULT_FILE)

    print("\nCONFIGURATION COMPARISON")
    print("-" * 65)

    for result in all_results:
        print(
            result["config"],
            "| Accuracy:", result["accuracy_percent"], "%",
            "| Abstention:", result["abstention_accuracy_percent"], "%"
        )


if __name__ == "__main__":
    main()
