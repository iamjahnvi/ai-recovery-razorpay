from datetime import datetime, date


def process_checkout_abandonment(event):
    amount = event["amount"]

    return {
        "event_type": "checkout_abandoned",
        "customer": event["customer"],
        "amount": amount,
        "revenue_at_risk": amount,
        "recommended_action": "send_reminder"
    }


def process_overdue_receivable(event):
    due_date = datetime.strptime(
        event["due_date"],
        "%Y-%m-%d"
    ).date()

    days_overdue = (date.today() - due_date).days

    if days_overdue > 0:
        return {
            "event_type": "overdue_receivable",
            "customer": event["customer"],
            "amount": event["amount"],
            "days_overdue": days_overdue,
            "revenue_at_risk": event["amount"],
            "recommended_action": "send_payment_reminder"
        }

    return {
        "event_type": "overdue_receivable",
        "customer": event["customer"],
        "amount": event["amount"],
        "days_overdue": 0,
        "revenue_at_risk": 0,
        "recommended_action": "no_action"
    }