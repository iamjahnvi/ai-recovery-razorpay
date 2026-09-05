from batch_processor import process_batch
from recovery_metrics import calculate_recovery_metrics


def generate_agent_summary():

    results = process_batch()

    metrics = calculate_recovery_metrics(results)

    print("\n================================")
    print(" AI REVENUE RECOVERY AGENT")
    print("================================")

    print(
        "\nRevenue at risk: ₹",
        metrics["total_revenue_at_risk"]
    )

    print(
        "Recovered revenue: ₹",
        metrics["recovered_revenue"]
    )

    print(
        "Recovery rate:",
        metrics["recovery_rate"],
        "%"
    )

    print(
        "Events processed:",
        metrics["total_events"]
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

    print("\nAgent pipeline:")
    print("Detection → Risk → Decision → Execution → Recovery")


if __name__ == "__main__":
    generate_agent_summary()