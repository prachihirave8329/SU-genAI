
from app.records import get_by_id


def monthly_savings_calculator(drug_code, branded_price, tablets_per_day):

    # Find medicine using drug code
    medicine = get_by_id(drug_code)

    if medicine is None:
        return {"error": "Medicine not found"}

    # Check inputs
    if branded_price <= 0 or tablets_per_day <= 0:
        return {"error": "Enter positive values"}

    # Get Jan Aushadhi price and pack size
    jan_price = medicine["mrp_inr"]
    unit_size = medicine["unit_size"].lower()

    if "tablet" not in unit_size:
        return {"error": "This calculator supports tablets only"}

    pack_size = int(unit_size.split()[0])

    # Calculate cost per tablet
    jan_cost = jan_price / pack_size
    branded_cost = branded_price / pack_size

    # Calculate monthly cost
    monthly_tablets = tablets_per_day * 30

    jan_monthly = jan_cost * monthly_tablets
    branded_monthly = branded_cost * monthly_tablets

    # Calculate savings
    monthly_savings = branded_monthly - jan_monthly
    yearly_savings = monthly_savings * 12

    return {
        "medicine": medicine["generic_name"],
        "jan_monthly_cost": round(jan_monthly, 2),
        "branded_monthly_cost": round(branded_monthly, 2),
        "monthly_savings": round(monthly_savings, 2),
        "yearly_savings": round(yearly_savings, 2)
    }
