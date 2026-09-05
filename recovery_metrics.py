import json


def calculate_recovery_metrics(results):

    with open("recovery_outcomes.json", "r") as file:
        outcomes = json.load(file)

    outcome_map = {
        outcome["event_id"]: outcome
        for outcome in outcomes
    }

    total_at_risk = sum(
        result["revenue_at_risk"]
        for result in results
    )

    recovered_revenue = 0
    escalated = 0
    stopped = 0
    recovered_events = 0

    for result in results:

        outcome = outcome_map.get(result["event_id"])

        if outcome:

            if outcome["status"] == "recovered":
                recovered_revenue += outcome["recovered_amount"]
                recovered_events += 1

            elif outcome["status"] == "escalated":
                escalated += 1

        if result["decision"] == "stop":
            stopped += 1

    recovery_rate = (
        recovered_revenue / total_at_risk * 100
        if total_at_risk > 0
        else 0
    )

    return {
        "total_revenue_at_risk": round(total_at_risk, 2),
        "recovered_revenue": round(recovered_revenue, 2),
        "recovery_rate": round(recovery_rate, 2),
        "recovered_events": recovered_events,
        "escalated": escalated,
        "stopped": stopped,
        "total_events": len(results)
    }


def load_batch_results():

    try:
        with open("batch_results.json", "r") as file:
            return json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        return []


if __name__ == "__main__":

    results = load_batch_results()

    if not results:
        print("No batch results available.")
    else:

        metrics = calculate_recovery_metrics(results)

        print("\nRECOVERY METRICS")
        print("----------------")

        print(
            "Revenue at risk:",
            metrics["total_revenue_at_risk"]
        )

        print(
            "Recovered revenue:",
            metrics["recovered_revenue"]
        )

        print(
            "Recovery rate:",
            metrics["recovery_rate"],
            "%"
        )

        print(
            "Recovered events:",
            metrics["recovered_events"]
        )

        print(
            "Escalated:",
            metrics["escalated"]
        )

        print(
            "Stopped:",
            metrics["stopped"]
        )

        print(
            "Total events:",
            metrics["total_events"]
        )