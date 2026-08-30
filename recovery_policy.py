import random

def recovery_policy(payment: dict) -> dict:

    """
    Deterministic rule-based recovery decision.
    Returns a dict: {action,reason,retry_after_minutes}
    Actions: "retry" | "ask_customer" | "stop"

    """

    failure_reason = payment["failure_reason"]
    attempts = payment["previous_attempts"]
    minutes = payment["minutes_since_failure"]
    tier= payment["customer_tier"]
    subscription= payment["subscription"]

    non_retryable_reasons = {"incorrect_CVC" , "mismatched_card_number", "expired_card"}
    if failure_reason in non_retryable_reasons:
        return {
            "action": "ask_customer" ,
            "reason": f"{failure_reason} cannot be fixed   by retrying - needs updated card details." ,
            "retry_after_minutes" :0
        }

    if attempts >= 5:
        return {
            "action" : "stop" ,
            "reason" : "Maximun retry attempts exceeded - escalate to write-off/manual review.",
            "retry_after_minutes" :0
        }

    if attempts >=3:
        return{
            "action": "ask_customer",
            "reason":"Multiple automated retries failed-needs customer intervention.",
            "retry_after_minutes" :0
        }

    if failure_reason == "insufficient_funds":
        if tier in ("vip", "vvip", "enterprise"):
            return {
                "action": "ask_customer",
                "reason": "High-value customer with insufficient funds — prefer manual outreach over silent retry.",
                "retry_after_minutes" :0
            }
        return {
            "action": "retry",
            "reason": "Insufficient funds — retry after a cooldown to allow balance top-up (e.g. payday cycle)",
            "retry_after_minutes": 1440,  # ~24 hours
        }
    
    if failure_reason in ("bank_declined", "processing_error"):
        if minutes <= 5:
            return {
                "action": "retry",
                "reason": "Transient failure detected very recently — quick retry likely to succeed",
                "retry_after_minutes": 5,
            }
        if minutes <= 30:
            return {
                "action": "retry",
                "reason": "Transient failure — retry with short backoff",
                "retry_after_minutes": 15,
            }
        return {
            "action": "ask_customer",
            "reason": "Transient failure persisting beyond 30 minutes — likely not self-resolving.",
            "retry_after_minutes" :0
        }

    if subscription and attempts < 3:
        return {
            "action": "retry",
            "reason": "Active subscription — retry to avoid involuntary churn before asking customer",
            "retry_after_minutes": 60,
        }

    return {
        "action": "stop",
        "reason": "No matching recovery rule — defaulting to stop for manual review",
        "retry_after_minutes" :0
    }

