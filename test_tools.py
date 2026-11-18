
from app.tools import monthly_savings_calculator

result = monthly_savings_calculator(
    drug_code="SAMPLE001",
    branded_price=100,
    tablets_per_day=2
)

print(result)
