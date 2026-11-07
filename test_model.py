
from app.models import Record

medicine = Record(
    drug_code="1001",
    generic_name="Paracetamol",
    strength="500 mg",
    unit_size="10 tablets",
    mrp_inr=10.50,
    therapeutic_group="Painkiller"
)

print(medicine)
print(medicine.generic_name)
print(medicine.mrp_inr)
