
import json
from pathlib import Path

from app.smart_search import search_records
from app.services import generate_chat_answer


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "records.json"
EVAL_DIR = BASE_DIR / "eval"
PROMPTS_DIR = BASE_DIR / "prompts"


QUESTIONS = [
    {
        "id": "Q1",
        "question": "What is JanAushadhiFinder?",
        "task": "general"
    },
    {
        "id": "Q2",
        "question": "Where can I find a nearby Jan Aushadhi Kendra?",
        "task": "general"
    },
    {
        "id": "Q3",
        "question": "Where can I check medicine information?",
        "task": "general"
    },
    {
        "id": "Q4",
        "question": "What is the price of Paracetamol 500 mg?",
        "task": "medicine"
    },
    {
        "id": "Q5",
        "question": "What is the strength and unit size of Paracetamol?",
        "task": "medicine"
    },
    {
        "id": "Q6",
        "question": "Is Paracetamol 500 mg currently available in stock at my nearest Jan Aushadhi Kendra?",
        "task": "general"
    },
    {
        "id": "Q7",
        "question": "What is the drug code of Paracetamol?",
        "task": "medicine"
    },
    {
        "id": "Q8",
        "question": "Which medicines belong to the Painkiller therapeutic group?",
        "task": "medicine"
    },
    {
        "id": "Q9",
        "question": "How much does a particular generic medicine cost?",
        "task": "medicine"
    },
    {
        "id": "Q10",
        "question": "Can I search for a medicine using its generic name?",
        "task": "medicine"
    }
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_text(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def evaluate_prompt(prompt_name, system_prompt, records):

    results = []

    print(f"\nEvaluating {prompt_name}")
    print("-" * 50)

    for item in QUESTIONS:

        question = item["question"]
        task = item["task"]

        # Reproduce the same retrieval logic as /chat.
        if task == "medicine":
            matching_records = search_records(
                question,
                records
            )
            context_records = matching_records[:3]
        else:
            context_records = []

        try:
            response = generate_chat_answer(
                question=question,
                records=context_records,
                task=task,
                system_prompt_override=system_prompt
            )

            result = {
                "id": item["id"],
                "question": question,
                "task": task,
                "retrieved_records": context_records,
                "response": response,
                "status": "success"
            }

            print(f"{item['id']}: SUCCESS")

        except Exception as error:

            result = {
                "id": item["id"],
                "question": question,
                "task": task,
                "retrieved_records": context_records,
                "response": None,
                "status": "failed",
                "error": str(error)
            }

            print(f"{item['id']}: FAILED - {error}")

        results.append(result)

    return results


def main():

    records = load_json(DATA_FILE)

    # Version 1: Basic prompt
    prompt_v1 = load_text(
        EVAL_DIR / "system_v1.txt"
    )

    # Version 2: Existing improved prompt
    prompt_v2 = load_text(
        PROMPTS_DIR / "system.txt"
    )

    results_v1 = evaluate_prompt(
        "Version 1",
        prompt_v1,
        records
    )

    results_v2 = evaluate_prompt(
        "Version 2",
        prompt_v2,
        records
    )

    final_results = {
        "evaluation": "JanAushadhiFinder Prompt Comparison",
        "model_provider": "Configured provider from .env",
        "total_questions": len(QUESTIONS),
        "version_1": results_v1,
        "version_2": results_v2
    }

    output_file = EVAL_DIR / "results.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            final_results,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n" + "=" * 50)
    print("PROMPT EVALUATION COMPLETED")
    print("=" * 50)

    print(f"Version 1: {len(results_v1)} questions")
    print(f"Version 2: {len(results_v2)} questions")
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()
