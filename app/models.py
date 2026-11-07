
from dataclasses import dataclass


@dataclass
class Record:
    drug_code: str
    generic_name: str
    strength: str
    unit_size: str
    mrp_inr: float
    therapeutic_group: str
