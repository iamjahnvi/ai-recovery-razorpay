def execute_recovery(event, decision):
    """
    Execute a bounded recovery action.

    This is a sandbox execution layer.
    It does not charge customers or perform real payment retries.
    """

    # Support both dictionary decisions and simple action strings
    if isinstance(decision, dict):
        action = decision["action"]
    else:
        action = decision

    if action == "retry":
        retry_after = (
            decision.get("retry_after_minutes", 0)
            if isinstance(decision, dict)
            else 0
        )

        return {
            "success": False,
            "result": "retry_pending",
            "message": f"Retry scheduled after {retry_after} minutes."
        }

    if action == "send_reminder":
        return {
            "success": True,
            "result": "reminder_scheduled",
            "message": "Checkout recovery reminder scheduled."
        }

    if action == "send_payment_reminder":
        return {
            "success": True,
            "result": "reminder_scheduled",
            "message": "Payment collection reminder scheduled."
        }

    if action == "ask_customer":
        return {
            "success": True,
            "result": "customer_action_required",
            "message": "Customer intervention required."
        }

    if action == "stop":
        return {
            "success": True,
            "result": "recovery_stopped",
            "message": "Recovery stopped and sent for manual review."
        }

    return {
        "success": False,
        "result": "unknown_action",
        "message": "Unknown recovery action."
    }