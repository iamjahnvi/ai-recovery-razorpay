import json

from recovery_policy import recovery_policy
from risk_engine import calculate_revenue_risk
from recovery_executor import execute_recovery
from idempotency import is_processed, mark_processed

from event_processor import (
    process_checkout_abandonment,
    process_overdue_receivable
)


BATCH_RESULTS_FILE = "batch_results.json"


def save_audit_event(result):
    try:
        with open("recovery_history.json", "r") as file:
            history = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    history.append(result)

    with open("recovery_history.json", "w") as file:
        json.dump(history, file, indent=4)


def save_batch_results(results):
    with open(BATCH_RESULTS_FILE, "w") as file:
        json.dump(results, file, indent=4)


def process_batch():

    with open("batch_events.json", "r") as file:
        events = json.load(file)

    results = []

    for event in events:

        event_id = event["event_id"]

        if is_processed(event_id):
            print(f"Skipping {event_id} — already processed.")
            continue

        # -----------------------------
        # PAYMENT / SUBSCRIPTION FAILURE
        # -----------------------------

        if event["event_type"] in (
            "payment_failed",
            "subscription_failed"
        ):

            payment = {
                "payment_id": event["event_id"],
                "amount": event["amount"] * 100,
                "currency": event["currency"],
                "status": "failed",
                "payment_method": "unknown",
                "failure_reason": event["failure_reason"],
                "previous_attempts": event["previous_attempts"],
                "minutes_since_failure": 10,
                "customer_tier": event["customer_tier"],
                "subscription": event["subscription"],
                "lifetime_value": 0
            }

            risk = calculate_revenue_risk(payment)

            decision = recovery_policy(payment)

            execution = execute_recovery(
                payment,
                decision
            )

            result = {
                "event_id": event["event_id"],
                "event_type": event["event_type"],
                "amount": event["amount"],
                "revenue_at_risk": risk["revenue_at_risk"],
                "decision": decision["action"],
                "execution": execution["result"]
            }

        # -----------------------------
        # CHECKOUT ABANDONMENT
        # -----------------------------

        elif event["event_type"] == "checkout_abandoned":

            processed = process_checkout_abandonment(event)

            decision = processed["recommended_action"]

            execution = execute_recovery(
                event,
                decision
            )

            result = {
                "event_id": event["event_id"],
                "event_type": event["event_type"],
                "amount": processed["amount"],
                "revenue_at_risk": processed["revenue_at_risk"],
                "decision": decision,
                "execution": execution["result"]
            }

        # -----------------------------
        # OVERDUE RECEIVABLE
        # -----------------------------

        elif event["event_type"] == "overdue_receivable":

            processed = process_overdue_receivable(event)

            decision = processed["recommended_action"]

            execution = execute_recovery(
                event,
                decision
            )

            result = {
                "event_id": event["event_id"],
                "event_type": event["event_type"],
                "amount": processed["amount"],
                "revenue_at_risk": processed["revenue_at_risk"],
                "decision": decision,
                "execution": execution["result"]
            }

        else:
            continue

        results.append(result)

        save_audit_event(result)

        mark_processed(event_id)

    # Save only newly processed results
    if results:
        save_batch_results(results)

    return results


if __name__ == "__main__":

    results = process_batch()

    print("\nBATCH RECOVERY ANALYSIS")
    print("-----------------------")

    for result in results:
        print(result)