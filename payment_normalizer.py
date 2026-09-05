# This file's only job is: Razorpay's format → our agent's format

from datetime import datetime, timezone

def normalize_payment(razorpay_payment: dict, customer_profile: dict = None) -> dict:

    error_description = (
        razorpay_payment.get("error_description") or ""
    ).lower()

    error_source = (
        razorpay_payment.get("error_source") or ""
    ).lower()

    if "declined by the bank" in error_description or error_source == "bank":
        failure_reason = "bank_declined"

    elif "insufficient" in error_description:
        failure_reason = "insufficient_funds"

    elif "expired" in error_description:
        failure_reason = "expired_card"

    elif "cvc" in error_description:
        failure_reason = "incorrect_CVC"

    elif "card number" in error_description:
        failure_reason = "mismatched_card_number"

    elif razorpay_payment.get("status") == "failed":
        failure_reason = "processing_error"

    else:
        failure_reason = None

    created_at = razorpay_payment.get("created_at")

    if created_at:
        created_time = datetime.fromtimestamp(
            created_at,
            tz=timezone.utc
        )

        minutes_since_failure = int(
            (datetime.now(timezone.utc) - created_time).total_seconds() / 60
        )

    else :
        minutes_since_failure = 0   

    return {
        "payment_id": razorpay_payment["id"],
        "amount": razorpay_payment["amount"],
        "currency": razorpay_payment["currency"],
        "status": razorpay_payment["status"],
        "payment_method": razorpay_payment.get("method"),
        "failure_reason": failure_reason,

        # These aren't supplied by this API response yet.
        "previous_attempts": 0,
        "minutes_since_failure": minutes_since_failure,

        # Temporary until we get customer/subscription data
        "customer_tier": customer_profile.get("customer_tier", "free") if customer_profile else "free",
        "subscription": customer_profile.get("subscription", False) if customer_profile else False,
        "lifetime_value": customer_profile.get("lifetime_value", 0) if customer_profile else 0,
    }

    