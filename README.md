# JanAushadhiFinder

## Project Card

**Product:** JanAushadhiFinder is a platform concept that helps users discover nearby Jan Aushadhi Kendras and access information about affordable generic medicines.

**User:** Patients, caregivers, and people looking for affordable generic medicines.

**Problem:** People may not know where nearby Jan Aushadhi Kendras are located or where to find reliable medicine information.

**Data Source:** Official PMBI / Janaushadhi website, including Kendra location information and medicine catalogue details.

## Project Goal

To make information about affordable generic medicines and nearby Jan Aushadhi Kendras easier to access.

## Features

- Fetches information from official PMBI web pages.
- Cleans and processes medicine records.
- Stores structured medicine data in JSON format.
- Provides REST APIs using FastAPI.
- Retrieves all medicine records with optional limits.
- Retrieves individual records using drug codes.
- Searches medicine records using TF-IDF and cosine similarity.
- Accepts user questions through a POST API.
- Explores medicine data using Pandas.

## Technology Stack

- Python
- FastAPI
- Uvicorn
- Pandas
- Scikit-learn
- JSON
- Requests

## Project Structure

```text
SU-genAI/
├── app/
│   ├── main.py
│   ├── smart_search.py
│   ├── models.py
│   ├── records.py
│   ├── ingest.py
│   └── fetch.py
├── analysis/
│   └── explore.py
├── data/
│   ├── raw/
│   └── records.json
├── requirements.txt
└── README.md
```

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/prachihirave8329/SU-genAI.git
cd SU-genAI
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the FastAPI application

```bash
python -m uvicorn app.main:app --reload
```

### 5. Open API documentation

Visit:

http://127.0.0.1:8000/docs

### 6. Run data exploration

Open another terminal, activate the virtual environment, and execute:

```bash
python analysis/explore.py
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check API health |
| GET | `/records` | Retrieve all records |
| GET | `/records?limit=2` | Retrieve limited records |
| GET | `/records/{id}` | Retrieve record by drug code |
| GET | `/search?q=paracetamol` | Search medicine records |
| POST | `/questions` | Ask questions about medicine records |

## Note

This project provides information only. It does not prescribe medicines or recommend substitutions. Search results are based on text similarity and should not be treated as medical advice.


## RAG Evaluation – Day 8

### Evaluation Dataset
- Total questions: 15
- Answerable questions: 13
- Abstention questions: 2
- Evaluation method: Compare retrieval configurations using the same question set.

### Configuration Comparison

| Parameter | Config A | Config B |
|---|---:|---:|
| Chunk Size | 500 | 300 |
| Chunk Overlap | 50 | 50 |
| Top K | 3 | 5 |
| Accuracy | 66.67% | 86.67% |
| Abstention Accuracy | 100% | 100% |

### Evaluation Results

Config B achieved the highest accuracy of 86.67%, compared with 66.67% for Config A.

Config B correctly answered 13 out of 15 questions and correctly abstained on both questions requiring unavailable real-time stock information.

### Conclusion

Config B was selected as the better-performing configuration in this evaluation.

Smaller chunks and a higher retrieval count provided more relevant context for answering questions. Since both chunk size and Top K changed together, further controlled experiments are needed to measure their individual effects.

### Evaluation Output

Results are saved in:

`eval/rag_eval_results.json`
