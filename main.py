from dotenv import load_dotenv
import os
import json

import razorpay
from openai import OpenAI

from recovery_policy import recovery_policy
from payment_normalizer import normalize_payment
from recovery_executor import execute_recovery
from risk_engine import calculate_revenue_risk

# Load environment variables
load_dotenv()


# Groq AI client
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


# Razorpay client
razorpay_client = razorpay.Client(
    auth=(
        os.getenv("TEST_API_KEY"),
        os.getenv("TEST_KEY_SECRET")
    )
)


# Get payment ID
payment_id = input("Enter Razorpay payment ID: ")


# Fetch real payment from Razorpay
razorpay_payment = razorpay_client.payment.fetch(payment_id)


# Convert Razorpay response into our internal format
with open("customer_profiles.json", "r") as file:
    customer_profiles = json.load(file)

customer_email = razorpay_payment.get("email")
customer_profile = customer_profiles.get(customer_email)

payment = normalize_payment(
    razorpay_payment,
    customer_profile
)


# Load recovery history
with open("recovery_history.json", "r") as file:
    recovery_history = json.load(file)


# Count previous retry attempts
previous_attempts = [
    event
    for event in recovery_history
    if event["payment_id"] == payment["payment_id"]
    and event["action"] == "retry"
]

payment["previous_attempts"] = len(previous_attempts)
risk = calculate_revenue_risk(payment)

print("\nPAYMENT FOR RECOVERY ENGINE:")
print(payment)


# AI recovery decision engine
decision = recovery_policy(payment)


print("\nRECOVERY DECISION:")
print("ACTION:", decision["action"])
print("REASON:", decision["reason"])
print("RETRY AFTER:", decision["retry_after_minutes"], "minutes")


# Execute bounded recovery action
execution = execute_recovery(payment, decision)


print("\nRECOVERY EXECUTION:")
print("RESULT:", execution["result"])
print("MESSAGE:", execution["message"])


# Generate customer-facing message when intervention is required
if decision["action"] == "ask_customer":

    message_response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": """
                You are a payment recovery assistant.

                Write a short, polite customer-facing message explaining
                that their payment could not be completed.

                Do not mention internal rules, retry attempts, AI,
                or technical details.

                Keep it under 100 words.
                """
            },
            {
                "role": "user",
                "content": f"""
                Payment amount: {payment["amount"] / 100:.2f} {payment["currency"]}
                Payment method: {payment["payment_method"]}
                Recovery reason: {decision["reason"]}
                """
            }
        ]
    )

    customer_message = message_response.choices[0].message.content

    print("\nCUSTOMER MESSAGE:")
    print(customer_message)


# Determine audit result
event_result = execution["result"]

if decision["action"] == "ask_customer":
    event_result = "customer_notified"


# Save recovery event
recovery_history.append({
    "payment_id": payment["payment_id"],
    "attempt": payment["previous_attempts"],
    "action": decision["action"],
    "reason": decision["reason"],
    "result": event_result
})


# Show history for this payment
current_payment_history = [
    event
    for event in recovery_history
    if event["payment_id"] == payment["payment_id"]
]


print("\nRECOVERY HISTORY")

for event in current_payment_history:
    print("ATTEMPT:", event["attempt"])
    print("ACTION:", event["action"])
    print("REASON:", event["reason"])
    print("PAYMENT_ID:", event["payment_id"])
    print("RESULT:", event["result"])


# Persist history
with open("recovery_history.json", "w") as file:
    json.dump(
        recovery_history,
        file,
        indent=4
    )

print("\nREVENUE RISK:")
print("AMOUNT:", risk["amount"], payment["currency"])
print("RECOVERY PROBABILITY:", risk["recovery_probability"])
print("REVENUE AT RISK:", risk["revenue_at_risk"], payment["currency"])