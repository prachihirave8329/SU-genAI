
import json
from pathlib import Path

import pandas as pd


# Get project directory
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "records.json"


# Load medicine records
with open(DATA_FILE, "r", encoding="utf-8") as file:
    records = json.load(file)


# Convert JSON records into DataFrame
df = pd.DataFrame(records)


print("\n===== JAN AUSHADHIFINDER DATA EXPLORATION =====")

# Fact 1: Total records
print("\nFact 1: Total medicine records")
print(len(df))


# Fact 2: Cheapest medicine
cheapest = df.loc[df["mrp_inr"].idxmin()]

print("\nFact 2: Cheapest medicine")
print("Name:", cheapest["generic_name"])
print("Price: Rs.", cheapest["mrp_inr"])


# Fact 3: Records by therapeutic group
print("\nFact 3: Records by therapeutic group")
print(df["therapeutic_group"].value_counts())


print("\n===== EXPLORATION COMPLETED =====")

