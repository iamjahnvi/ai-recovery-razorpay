from datetime import datetime, timezone

# It's extracting the facts our policy actually needs.

def map_razorpay_payment(data: dict) -> dict:
    error_description = data.get("error_description", "").lower()

    if "declined by the bank" in error_description:
        failure_reason = "bank_declined"
    elif "processing" in error_description:
        failure_reason = "processing_error"
    elif "insufficient" in error_description:
        failure_reason = "insufficient_funds"
    else:
        failure_reason = data.get("error_reason", "unknown")

    created_at = data.get("created_at")

    if created_at:
        created_time = datetime.fromtimestamp(
            created_at,
            tz=timezone.utc
        )
        minutes_since_failure = int(
            (datetime.now(timezone.utc) - created_time).total_seconds() / 60
        )
    else:
        minutes_since_failure = 0

    return {
        "payment_id": data["id"],
        "amount": data["amount"],
        "currency": data["currency"],
        "status": data["status"],
        "payment_method": data["method"],
        "failure_reason": failure_reason,
        "previous_attempts": 0,
        "minutes_since_failure": minutes_since_failure,

        # Temporary business-profile values
        "customer_tier": "free",
        "subscription": False,
    }