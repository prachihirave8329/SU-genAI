
from data.sample_records import medicine_records


# Load all medicine records
def load_records():
    return medicine_records


# Search medicine by name
def search(keyword):
    results = []

    for medicine in medicine_records:
        if keyword.lower() in medicine["generic_name"].lower():
            results.append(medicine)

    return results


# Count medicines by category
def count_by():
    category_count = {}

    for medicine in medicine_records:
        category = medicine["therapeutic_group"]

        if category in category_count:
            category_count[category] += 1
        else:
            category_count[category] = 1

    return category_count


# Find medicine using drug code
def get_by_id(drug_code):
    for medicine in medicine_records:
        if medicine["drug_code"] == drug_code:
            return medicine

    return None
