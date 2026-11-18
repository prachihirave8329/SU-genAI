
from app.records import get_by_id


def monthly_savings_calculator(
    drug_code, branded_price, branded_pack_size, tablets_per_day
):
    medicine = get_by_id(drug_code)

    if medicine is None:
        return {"error": "Medicine not found"}

    if branded_price <= 0 or branded_pack_size <= 0 or tablets_per_day <= 0:
        return {"error": "Enter valid positive values"}

    if "tablet" not in medicine["unit_size"].lower():
        return {"error": "Only tablet medicines are supported"}

    jan_pack_size = int(medicine["unit_size"].split()[0])

    jan_cost = medicine["mrp_inr"] / jan_pack_size
    branded_cost = branded_price / branded_pack_size

    monthly_tablets = tablets_per_day * 30

    jan_monthly = jan_cost * monthly_tablets
    branded_monthly = branded_cost * monthly_tablets

    savings = branded_monthly - jan_monthly

    return {
        "medicine": medicine["generic_name"],
        "strength": medicine["strength"],
        "jan_monthly_cost": round(jan_monthly, 2),
        "branded_monthly_cost": round(branded_monthly, 2),
        "monthly_savings": round(savings, 2),
        "yearly_savings": round(savings * 12, 2)
    }
