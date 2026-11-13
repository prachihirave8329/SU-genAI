
import json
from pathlib import Path

from app.llm import generate_response


BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"


def load_prompt(filename: str) -> str:
    prompt_path = PROMPTS_DIR / filename

    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()

def generate_chat_answer(
    question: str,
    records: list,
    task: str,
    system_prompt_override: str | None = None
):
    # Load the system prompt
    system_prompt = load_prompt("system.txt")

    # Select the task-specific prompt
    if task == "medicine":
        task_prompt = load_prompt("task_medicine.txt")

    elif task == "general":
        task_prompt = load_prompt("task_general.txt")

    else:
        raise ValueError("Task must be medicine or general")

    # Prepare the context
    context = json.dumps(records, ensure_ascii=False, indent=2)

    # Insert the question and retrieved records
    user_prompt = task_prompt.format(
        records=context,
        question=question
    )

    # Call the selected LLM provider
    raw_response = generate_response(
        system_prompt,
        user_prompt
    )

    # Convert JSON text into a Python dictionary
    try:
        result = json.loads(raw_response)

    except json.JSONDecodeError:
        raise ValueError("LLM returned invalid JSON")

    # Validate the response structure
    if not isinstance(result, dict):
        raise ValueError("LLM response must be a JSON object")

    answer = result.get("answer")
    confidence = result.get("confidence")
    follow_up = result.get("follow_up")

    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("Invalid answer returned by LLM")

    if (
        isinstance(confidence, bool)
        or not isinstance(confidence, (int, float))
        or not 0 <= confidence <= 1
    ):
        raise ValueError("Invalid confidence returned by LLM")

    if not isinstance(follow_up, str):
        raise ValueError("Invalid follow_up returned by LLM")

    return {
        "answer": answer,
        "confidence": float(confidence),
        "follow_up": follow_up
    }
