
import json

from app.llm import generate_response
from app.vectorstore import semantic_search
from app.tools import monthly_savings_calculator


# Step 1: LLM selects a tool
def choose_tool(question):

    system_prompt = """
    You are a tool selection assistant.

    Available tools:
    1. rag_search - for Jan Aushadhi information.
    2. savings_calculator - for medicine cost and savings.
    3. unknown - for unrelated questions.

    Return JSON only.

    Example:
    {"tool": "rag_search"}
    """

    response = generate_response(system_prompt, question)

    result = json.loads(response)

    tool = result.get("tool")

    if tool not in ["rag_search", "savings_calculator", "unknown"]:
        return "unknown"

    return tool


# Step 2: RAG Search Tool
def rag_search(question):

    results = semantic_search(question, n_results=3)

    documents = results["documents"][0]

    return documents


# Step 3: Savings Calculator Tool
def savings_tool(drug_code, branded_price, tablets_per_day):

    return monthly_savings_calculator(
        drug_code,
        branded_price,
        tablets_per_day
    )


# Step 4: LLM generates the final answer
def generate_final_answer(question, tool_result):

    system_prompt = """
    You are a helpful Jan Aushadhi assistant.

    Answer the user's question using the tool result.

    Rules:
    - Use simple language.
    - Do not invent information.
    - If information is missing, say so.
    - For savings, clearly mention monthly and yearly savings.
    - Do not recommend changing medicines or doses.
    - Return JSON only in this format:

    {"answer": "Your final answer"}
    """

    user_prompt = f"""
    User Question:
    {question}

    Tool Result:
    {json.dumps(tool_result, ensure_ascii=False)}

    Prepare a helpful answer for the user.
    """

    response = generate_response(system_prompt, user_prompt)

    result = json.loads(response)

    return result.get("answer", "Sorry, I could not prepare an answer.")


# Step 5: Complete Agent Loop
def agent_loop():

    print("Jan Aushadhi AI Agent Started!")

    while True:

        question = input("\nYou: ")

        if question.lower() == "exit":
            print("Agent stopped.")
            break

        try:

            # REASON: Select a tool
            tool = choose_tool(question)

            print("\nSelected Tool:", tool)

            # ACT: Execute the selected tool
            if tool == "rag_search":

                tool_result = rag_search(question)

            elif tool == "savings_calculator":

                drug_code = input("Enter drug code: ")
                branded_price = float(input("Enter branded pack price: "))
                tablets_per_day = float(input("Enter tablets per day: "))

                tool_result = savings_tool(
                    drug_code,
                    branded_price,
                    tablets_per_day
                )

            else:

                tool_result = {
                    "message": "Question is outside the supported topics."
                }

            # OBSERVE: LLM receives the tool result
            print("\nGenerating final answer...")

            answer = generate_final_answer(
                question,
                tool_result
            )

            print("\nAgent:", answer)

        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:

            print("Error:", error)


if __name__ == "__main__":
    agent_loop()
