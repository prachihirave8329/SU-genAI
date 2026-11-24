
from app.vectorstore import expand_query


def test_existing_faq_query_expansion():
    query = "What is the purpose of PMBJP?"

    expanded = expand_query(query)

    assert "Pradhan Mantri Bhartiya Janaushadhi" in expanded
    assert "affordable prices" in expanded


def test_unknown_query_remains_unchanged():
    query = "Find Azithromycin tablets"

    assert expand_query(query) == query


def test_query_expansion_ignores_extra_spaces():
    query = "  What is Jan Aushadhi?  "

    expanded = expand_query(query)

    assert "PMBJP" in expanded

from app.vectorstore import _product_match_score


def test_combination_product_scores_higher_than_single_ingredient():
    query = "Find Metformin and Glimepiride combination tablets"

    combination = (
        "Metformin Hydrochloride Prolonged-release 500mg "
        "and Glimepiride 2mg Tablets IP"
    )

    single_ingredient = (
        "Metformin Hydrochloride Tablets IP 500mg"
    )

    assert _product_match_score(
        query, combination
    ) > _product_match_score(
        query, single_ingredient
    )


def test_matching_dosage_form_improves_product_score():
    query = "Find Azithromycin tablets"

    tablet = "Azithromycin Tablets IP 250 mg"
    suspension = "Azithromycin Oral Suspension 200 mg"

    assert _product_match_score(
        query, tablet
    ) > _product_match_score(
        query, suspension
    )


def test_exact_medicine_name_is_relevant():
    query = "Find Cetirizine syrup"

    relevant = "Cetirizine Syrup IP 5 mg per 5 ml"
    irrelevant = "Paracetamol Tablets IP 500mg"

    assert _product_match_score(
        query, relevant
    ) > _product_match_score(
        query, irrelevant
    )
