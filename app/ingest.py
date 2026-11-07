
import csv
import json
from pathlib import Path

from app.models import Record

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "raw" / "product_sample.csv"
OUTPUT_FILE = BASE_DIR / "data" / "records.json"


def ingest_products():

    records = []

    try:
        # Open CSV file
        with open(
            INPUT_FILE,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            # Ignore empty lines
            non_empty_lines = (
                line for line in file if line.strip()
            )

            # Read CSV data
            reader = csv.DictReader(non_empty_lines)

            # Clean column names
            if reader.fieldnames:
                reader.fieldnames = [
                    name.strip() for name in reader.fieldnames
                ]

            print("CSV Columns:", reader.fieldnames)

            # Process each product
            for row in reader:

                try:
                    record = Record(
                        drug_code=row["drug_code"].strip(),
                        generic_name=row["generic_name"].strip(),
                        strength=row["strength"].strip(),
                        unit_size=row["unit_size"].strip(),
                        mrp_inr=float(row["mrp_inr"]),
                        therapeutic_group=row["therapeutic_group"].strip()
                    )

                    # Validate records
                    if not record.drug_code:
                        raise ValueError("Missing drug code")

                    if not record.generic_name:
                        raise ValueError("Missing generic name")

                    if record.mrp_inr <= 0:
                        raise ValueError("Invalid MRP")

                    records.append(record)

                except (ValueError, KeyError, AttributeError) as error:
                    print(
                        f"Skipping invalid row: {row}. Reason: {error}"
                    )

        # Convert records into dictionaries
        output_data = [
            record.__dict__ for record in records
        ]

        # Create output directory if needed
        OUTPUT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Save records as JSON
        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                output_data,
                file,
                indent=4
            )

        print("\nIngestion completed!")
        print("Valid records:", len(records))
        print("Output file:", OUTPUT_FILE)

    except FileNotFoundError:
        print("Input CSV file not found:", INPUT_FILE)

    except OSError as error:
        print("File error:", error)


if __name__ == "__main__":
    ingest_products()
