
medicine_records = [

    # Diabetes medicines
    {
        "drug_code": "SAMPLE001",
        "generic_name": "Metformin",
        "strength": "500 mg",
        "unit_size": "10 tablets",
        "mrp_inr": 15.00,
        "therapeutic_group": "Diabetes"
    },
    {
        "drug_code": "SAMPLE002",
        "generic_name": "Metformin",
        "strength": "1000 mg",
        "unit_size": "10 tablets",
        "mrp_inr": 22.00,
        "therapeutic_group": "Diabetes"
    },
    {
        "drug_code": "SAMPLE003",
        "generic_name": "Glimepiride",
        "strength": "1 mg",
        "unit_size": "10 tablets",
        "mrp_inr": 12.00,
        "therapeutic_group": "Diabetes"
    },
    {
        "drug_code": "SAMPLE004",
        "generic_name": "Glimepiride",
        "strength": "2 mg",
        "unit_size": "10 tablets",
        "mrp_inr": 18.00,
        "therapeutic_group": "Diabetes"
    },
    {
        "drug_code": "SAMPLE005",
        "generic_name": "Gliclazide",
        "strength": "40 mg",
        "unit_size": "10 tablets",
        "mrp_inr": 20.00,
        "therapeutic_group": "Diabetes"
    },

    # Blood pressure medicines
    {
        "drug_code": "SAMPLE006",
        "generic_name": "Amlodipine",
        "strength": "5 mg",
        "unit_size": "10 tablets",
        "mrp_inr": 10.00,
        "therapeutic_group": "Blood Pressure"
    },
    {
        "drug_code": "SAMPLE007",
        "generic_name": "Amlodipine",
        "strength": "10 mg",
        "unit_size": "10 tablets",
        "mrp_inr": 15.00,
        "therapeutic_group": "Blood Pressure"
    },
    {
        "drug_code": "SAMPLE008",
        "generic_name": "Telmisartan",
        "strength": "20 mg",
        "unit_size": "10 tablets",
        "mrp_inr": 18.00,
        "therapeutic_group": "Blood Pressure"
    },
    {
        "drug_code": "SAMPLE009",
        "generic_name": "Telmisartan",
        "strength": "40 mg",
        "unit_size": "10 tablets",
        "mrp_inr": 25.00,
        "therapeutic_group": "Blood Pressure"
    },
    {
        "drug_code": "SAMPLE010",
        "generic_name": "Losartan",
        "strength": "50 mg",
        "unit_size": "10 tablets",
        "mrp_inr": 20.00,
        "therapeutic_group": "Blood Pressure"
    },

    # Painkillers and antipyretics
    {
        "drug_code": "SAMPLE011",
        "generic_name": "Paracetamol",
        "strength": "500 mg",
        "unit_size": "10 tablets",
        "mrp_inr": 8.00,
        "therapeutic_group": "Painkillers"
    },
    {
        "drug_code": "SAMPLE012",
        "generic_name": "Paracetamol",
        "strength": "650 mg",
        "unit_size": "10 tablets",
        "mrp_inr": 12.00,
        "therapeutic_group": "Painkillers"
    },
    {
        "drug_code": "SAMPLE013",
        "generic_name": "Aceclofenac",
        "strength": "100 mg",
        "unit_size": "10 tablets",
        "mrp_inr": 18.00,
        "therapeutic_group": "Painkillers"
    },
    {
        "drug_code": "SAMPLE014",
        "generic_name": "Ibuprofen",
        "strength": "400 mg",
        "unit_size": "10 tablets",
        "mrp_inr": 15.00,
        "therapeutic_group": "Painkillers"
    },
    {
        "drug_code": "SAMPLE015",
        "generic_name": "Diclofenac",
        "strength": "50 mg",
        "unit_size": "10 tablets",
        "mrp_inr": 16.00,
        "therapeutic_group": "Painkillers"
    },

    # Antacids and antibiotics
    {
        "drug_code": "SAMPLE016",
        "generic_name": "Pantoprazole",
        "strength": "40 mg",
        "unit_size": "10 tablets",
        "mrp_inr": 25.00,
        "therapeutic_group": "Antacids"
    },
    {
        "drug_code": "SAMPLE017",
        "generic_name": "Omeprazole",
        "strength": "20 mg",
        "unit_size": "10 capsules",
        "mrp_inr": 20.00,
        "therapeutic_group": "Antacids"
    },
    {
        "drug_code": "SAMPLE018",
        "generic_name": "Magaldrate",
        "strength": "400 mg",
        "unit_size": "10 tablets",
        "mrp_inr": 22.00,
        "therapeutic_group": "Antacids"
    },
    {
        "drug_code": "SAMPLE019",
        "generic_name": "Amoxicillin",
        "strength": "500 mg",
        "unit_size": "10 capsules",
        "mrp_inr": 35.00,
        "therapeutic_group": "Antibiotics"
    },
    {
        "drug_code": "SAMPLE020",
        "generic_name": "Azithromycin",
        "strength": "500 mg",
        "unit_size": "3 tablets",
        "mrp_inr": 30.00,
        "therapeutic_group": "Antibiotics"
    }

]

# Print all medicine records
print("\n----- All Medicine Records -----")

for medicine in medicine_records:
    print(medicine)


# Search medicine by keyword
keyword = input("\nEnter medicine name to search: ")

print("\n----- Search Results -----")

for medicine in medicine_records:
    if keyword.lower() in medicine["generic_name"].lower():
        print(medicine)


# Count medicines by category
print("\n----- Medicine Count by Category -----")

category_count = {}

for medicine in medicine_records:
    category = medicine["therapeutic_group"]

    if category in category_count:
        category_count[category] += 1
    else:
        category_count[category] = 1

for category, count in category_count.items():
    print(category, ":", count)
