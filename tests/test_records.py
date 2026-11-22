
from app.records import (
    count_by,
    get_by_id,
    load_records,
    search,
)
from app.smart_search import search_records
from app.tools import monthly_savings_calculator


def test_load_records():
    records = load_records()

    assert len(records) > 0


def test_search_medicine():
    results = search("metformin")

    assert len(results) > 0
    assert all(
        "metformin" in item["generic_name"].lower()
        for item in results
    )


def test_search_is_case_insensitive():
    results = search("METFORMIN")

    assert len(results) > 0


def test_count_by_category():
    counts = count_by()

    assert isinstance(counts, dict)
    assert "Diabetes" in counts
    assert counts["Diabetes"] > 0


def test_get_medicine_by_id():
    medicine = get_by_id("SAMPLE001")

    assert medicine is not None
    assert medicine["generic_name"] == "Metformin"


def test_get_invalid_medicine():
    medicine = get_by_id("INVALID999")

    assert medicine is None


def test_smart_search():
    records = load_records()

    results = search_records("Metformin 500 mg", records)

    assert len(results) > 0
    assert results[0]["generic_name"] == "Metformin"
    assert "similarity_score" in results[0]


def test_smart_search_empty_query():
    results = search_records("", load_records())

    assert results == []


def test_smart_search_exact_medicine_name():
    records = load_records()

    results = search_records("Metformin", records)

    assert len(results) >= 2
    assert all(
        item["generic_name"] == "Metformin"
        for item in results
    )


def test_smart_search_exact_strength():
    records = load_records()

    results = search_records("Metformin 500 mg", records)

    assert len(results) > 0
    assert results[0]["generic_name"] == "Metformin"
    assert results[0]["strength"] == "500 mg"


def test_smart_search_different_strength():
    records = load_records()

    results = search_records("Metformin 1000 mg", records)

    assert len(results) > 0
    assert results[0]["generic_name"] == "Metformin"
    assert results[0]["strength"] == "1000 mg"


def test_smart_search_unknown_medicine():
    records = load_records()

    results = search_records("UnknownMedicine", records)

    assert results == []


def test_savings_calculator():
    result = monthly_savings_calculator(
        "SAMPLE001",
        50,
        10,
        2
    )

    assert result["monthly_savings"] == 210.0
    assert result["yearly_savings"] == 2520.0


def test_savings_invalid_medicine():
    result = monthly_savings_calculator(
        "INVALID999",
        50,
        10,
        2
    )

    assert result == {"error": "Medicine not found"}


def test_savings_invalid_price():
    result = monthly_savings_calculator(
        "SAMPLE001",
        -50,
        10,
        2
    )

    assert result == {"error": "Enter valid positive values"}
def test_smart_search_excludes_unrelated_medicines():
    records = load_records()

    results = search_records("Metformin 500 mg", records)

    assert len(results) > 0
    assert all(
        item["generic_name"] == "Metformin"
        for item in results
    )