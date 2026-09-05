from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv

import os
import json
import hmac
import hashlib

from payment_normalizer import normalize_payment
from recovery_policy import recovery_policy
from recovery_executor import execute_recovery
from risk_engine import calculate_revenue_risk

from idempotency import is_processed, mark_processed


load_dotenv()

app = FastAPI(
    title="AI Revenue Recovery Agent"
)

WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")


def verify_webhook_signature(
    raw_body: bytes,
    signature: str
):
    if not WEBHOOK_SECRET:
        raise RuntimeError(
            "RAZORPAY_WEBHOOK_SECRET is not configured."
        )

    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        signature
    )


@app.get("/")
def home():

    return {
        "status": "running",
        "service": "AI Revenue Recovery Agent"
    }


@app.post("/webhook/payment-failed")
async def payment_failed(
    request: Request,
    payload: dict
):

    # 1. Read raw request body
    raw_body = await request.body()

    # 2. Get Razorpay signature
    signature = request.headers.get(
        "X-Razorpay-Signature"
    )

    if not signature:

        raise HTTPException(
            status_code=401,
            detail="Missing Razorpay webhook signature."
        )

    # 3. Verify signature
    try:

        valid_signature = verify_webhook_signature(
            raw_body,
            signature
        )

    except RuntimeError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    if not valid_signature:

        raise HTTPException(
            status_code=401,
            detail="Invalid Razorpay webhook signature."
        )

    # 4. Extract payment
    payment_data = (
        payload
        .get("payload", {})
        .get("payment", {})
        .get("entity")
    )

    if not payment_data:

        raise HTTPException(
            status_code=400,
            detail="Payment data not found."
        )

    payment_id = payment_data.get("id")

    if not payment_id:

        raise HTTPException(
            status_code=400,
            detail="Payment ID not found."
        )

    event_id = request.headers.get("X-Razorpay-Event-Id")

    if not event_id:
        raise HTTPException(
            status_code=400,
            detail="Missing Razorpay event ID"
    )

    if is_processed(event_id):
        return {
            "success": True,
            "message": "Event already processed.",
            "event_id": event_id
        }

    # 6. Load customer profile
    try:

        with open(
            "customer_profiles.json",
            "r"
        ) as file:

            customer_profiles = json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):

        customer_profiles = {}

    customer_email = payment_data.get("email")

    customer_profile = customer_profiles.get(
        customer_email
    )

    # 7. Normalize payment
    payment = normalize_payment(
        payment_data,
        customer_profile
    )

    # 8. Calculate risk
    risk = calculate_revenue_risk(
        payment
    )

    # 9. Determine recovery action
    decision = recovery_policy(
        payment
    )

    # 10. Execute bounded action
    execution = execute_recovery(
        payment,
        decision
    )

    # 11. Save audit event
    audit_event = {

        "event_id": event_id,
        "payment_id": payment_id,

        "event_type": "payment_failed",

        "amount": payment["amount"] / 100,

        "currency": payment["currency"],

        "customer_tier": payment["customer_tier"],

        "failure_reason": payment["failure_reason"],

        "revenue_at_risk": risk["revenue_at_risk"],

        "recovery_probability": risk[
            "recovery_probability"
        ],

        "decision": decision["action"],

        "execution": execution["result"]

    }

    try:

        with open(
            "recovery_history.json",
            "r"
        ) as file:

            history = json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):

        history = []

    history.append(audit_event)

    with open(
        "recovery_history.json",
        "w"
    ) as file:

        json.dump(
            history,
            file,
            indent=4
        )

    # 12. Mark event processed
    mark_processed(event_id)

    # 13. Return result
    return {

        "success": True,

        "payment_id": payment_id,

        "customer_tier": payment[
            "customer_tier"
        ],

        "subscription": payment[
            "subscription"
        ],

        "revenue_at_risk": risk[
            "revenue_at_risk"
        ],

        "recovery_probability": risk[
            "recovery_probability"
        ],

        "decision": decision,

        "execution": execution

    }


