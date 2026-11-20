
from app.tools import monthly_savings_calculator

# Calculate monthly and yearly savings
result = monthly_savings_calculator(
    drug_code="SAMPLE001",
    branded_price=100,
    branded_pack_size=10,
    tablets_per_day=2
)

# Display the result
print("\nJan Aushadhi Monthly Savings Calculator")
print("---------------------------------------")

if "error" in result:
    print("Error:", result["error"])
else:
    print("Medicine:", result["medicine"])
    print("Strength:", result["strength"])
    print("Jan Aushadhi Monthly Cost: ₹", result["jan_monthly_cost"])
    print("Branded Monthly Cost: ₹", result["branded_monthly_cost"])
    print("Monthly Savings: ₹", result["monthly_savings"])
    print("Yearly Savings: ₹", result["yearly_savings"])
