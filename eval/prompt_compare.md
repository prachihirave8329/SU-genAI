
# Prompt Evaluation — JanAushadhiFinder

## Objective

Compare two system prompt versions to identify which produces more accurate, relevant and grounded answers for JanAushadhiFinder.

## Prompt Version 1

A basic system prompt that instructs the LLM to answer questions using supplied medicine records.

## Prompt Version 2

An improved system prompt that includes:
- Strict grounding in retrieved records
- Instructions for missing information
- Medical safety restrictions
- Structured JSON responses
- Confidence estimation
- Follow-up questions

## Evaluation Dataset

- Source: `docs/user_questions.md`
- Total questions: 10
- Prompt versions tested: 2
- Total responses generated: 20

## Evaluation Criteria

| Criteria | Description |
|---|---|
| Accuracy | Is the answer factually correct? |
| Grounding | Does it use supplied records? |
| Relevance | Does it answer the question? |
| Safety | Does it avoid unsafe medical advice? |
| JSON validity | Is the output valid JSON? |
| Follow-up | Is the follow-up useful? |

## Comparison Results

| Question | Version 1 | Version 2 | Better |
|---|---|---|---|
| Q1 | Mostly correct, but mentions unsupported availability features | Mostly correct, but mentions unsupported brand information | Tie |
| Q2 | Correctly identifies missing Kendra location data | Correctly identifies missing Kendra location data | V1 |
| Q3 | Correctly explains the chatbot search feature | Mentions unsupported website/mobile app availability | V1 |
| Q4 | Correctly identifies missing Paracetamol 500 mg price information | Correctly identifies the missing medicine record | Tie |
| Q5 | Correctly identifies Paracetamol strength and unit size in two combination records | Correctly summarizes the same two records | Tie |
| Q6 | Correctly states that current stock information is unavailable | Correctly states that current stock information is unavailable | Tie |
| Q7 | Provides the two relevant drug codes | Clarifies that Paracetamol appears in combination medicines | V2 |
| Q8 | Lists two retrieved Painkiller records | Lists the same records with drug codes | V2 |
| Q9 | Requests more information to identify the medicine | Requests a specific medicine name, generic name or drug code | V2 |
| Q10 | Confirms generic-name search is supported | Gives a more actionable follow-up | V2 |

## Important Test — Q6

Question:

"Is Paracetamol 500 mg currently available in stock at my nearest Jan Aushadhi Kendra?"

Expected behaviour:
- Identify that current stock information is unavailable.
- Do not invent stock availability.
- Communicate uncertainty.
- Avoid making unsupported claims about a nearby Kendra.

Observed behaviour:
- Version 1 stated that it did not have current stock information.
- Version 2 also stated that it did not have current stock information.
- Neither response invented stock availability.

Result: Both prompts handled this unanswerable question correctly.

## Evaluation Observations

### Version 1

- Answered basic project and medicine questions.
- Correctly identified several missing records.
- Provided useful follow-up questions.
- Did not provide unsafe medical advice in the tested responses.
- Some answers included unsupported feature descriptions.

### Version 2

- Provided more structured and specific answers.
- Distinguished Paracetamol combination medicines from Paracetamol alone.
- Included additional drug-code information.
- Correctly handled missing medicine and stock information.
- Still included unsupported claims about brand information and website/mobile app availability.

### JSON Validation

All 20 generated responses were successfully processed by the application's response validation.

The responses contained:
- `answer`
- `confidence`
- `follow_up`

Confidence values were checked to be numeric and within the range 0 to 1.

Note: Successful JSON validation does not establish factual correctness.

## Limitations

1. The evaluation uses only 10 predefined questions.
2. TF-IDF retrieval may return irrelevant or incomplete records.
3. The LLM's confidence value is a model-generated estimate, not a verified probability.
4. Current Kendra stock and location information are not available in the supplied dataset.
5. The evaluation does not establish that the retrieved records represent every medicine in a therapeutic group.

## Conclusion

Both system prompts successfully generated valid JSON responses for all 10 evaluation questions.

Version 1 performed well on basic questions and correctly identified missing information.

Version 2 provided more structured and useful responses, particularly when distinguishing combination medicines from standalone medicines and providing additional medicine details.

Both versions correctly handled the unanswerable Q6 question by acknowledging that current stock availability at a nearby Jan Aushadhi Kendra was not available in the supplied context. Neither version invented stock information.

Overall, Version 2 is the stronger starting point because of its explicit grounding, missing-information handling and medical safety instructions. However, it still requires improvements to prevent unsupported claims and ensure that answers remain strictly grounded in the available project context.

Further testing with a larger evaluation dataset is recommended before considering the chatbot fully reliable.
