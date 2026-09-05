from event_processor import (
    process_checkout_abandonment,
    process_overdue_receivable
)


checkout = {
    "customer": "customer_001",
    "amount": 5000
}

overdue = {
    "customer": "customer_002",
    "amount": 12000,
    "due_date": "2026-08-20"
}


print("\nCHECKOUT ABANDONMENT")
print(process_checkout_abandonment(checkout))


print("\nOVERDUE RECEIVABLE")
print(process_overdue_receivable(overdue))