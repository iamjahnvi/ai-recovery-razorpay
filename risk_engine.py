def calculate_revenue_risk(payment):
    amount = payment["amount"] / 100

    if payment["failure_reason"] == "insufficient_funds":
        recovery_probability = 0.60

    elif payment["failure_reason"] == "processing_error":
        recovery_probability = 0.70

    elif payment["failure_reason"] == "bank_declined":
        recovery_probability = 0.40

    else:
        recovery_probability = 0.20

    if payment["customer_tier"] in ("vip", "vvip", "enterprise"):
        recovery_probability += 0.10

    recovery_probability = min(recovery_probability, 0.95)

    revenue_at_risk = amount * recovery_probability

    return {
        "amount": amount,
        "recovery_probability": recovery_probability,
        "revenue_at_risk": round(revenue_at_risk, 2)
    }