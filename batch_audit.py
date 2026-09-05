import json


def show_audit_trail():

    try:
        with open("recovery_history.json", "r") as file:
            history = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    print("\nRECOVERY AUDIT TRAIL")
    print("--------------------")

    if not history:
        print("No recovery events recorded.")
        return

    for event in history:

        print("\nEvent ID:", event.get("event_id"))
        print("Event Type:", event.get("event_type"))
        print("Amount:", event.get("amount"))
        print("Revenue at Risk:", event.get("revenue_at_risk"))
        print("Decision:", event.get("decision"))
        print("Execution:", event.get("execution"))


if __name__ == "__main__":
    show_audit_trail()