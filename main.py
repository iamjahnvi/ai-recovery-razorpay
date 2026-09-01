from dotenv import load_dotenv
import os
import random
import json
import uuid
from recovery_policy import recovery_policy
from recovery_stimulator import stimulate_retry

load_dotenv()
# python, go inside .env and load the secrets.
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

possible_failure_reasons = [
    "incorrect_CVC",
    "mismatched_card_number",
    "expired_card",
    "insufficient_funds",
    "processing_error",
    "bank_declined",
]

possible_currency = ["USD", "INR", "MYR", "SGD"]

possible_customer_tier = ["vip", "vvip", "free", "premium", "enterprise"]

possible_card_brand = [
    "Visa",
    "Mastercard",
    "American Express",
    "RuPay",
    "Diners Club",
    "Discover",
    "Amex",
]

possible_payment_method_type = [
    "Credit Card",
    "Debit Card",
    "UPI",
    "Net Banking",
    "Digital Wallet",
    "EMI",
    "Cardless EMI",
    "Pay Later",
    "Bank Transfer",
    "QR Code",
    "International Payments",
    "Contactless / Tap & Pay",
]

is_subscription = [True, False]

payment = {
    "amount": random.randint(1000, 10000),
    "failure_reason": random.choice(possible_failure_reasons),
    "previous_attempts": random.randint(0, 2),
    "minutes_since_failure": random.randint(1, 5),
    "currency": random.choice(possible_currency),
    "customer_tier": random.choice(possible_customer_tier),
    "card_brand": random.choice(possible_card_brand),
    "payment_method": random.choice(possible_payment_method_type),
    "subscription": random.choice(is_subscription),
    "status": "failed",
    "payment_id": str(uuid.uuid4()),
}


with open("recovery_history.json", "r") as file:
    recovery_history = json.load(file)

decision = recovery_policy(payment)

if decision["action"] == "retry":

    print("\nRETRY SCHEDULED")
    print("Retry after:", decision["retry_after_minutes"], "minutes")

    result = stimulate_retry(payment)

    print("RETRY RESULT:", result["reason"])

    if result["success"]:
        payment["status"] = "recovered"
        print("PAYMENT STATUS: RECOVERED")

    else:
        payment["previous_attempts"] += 1
        print("ATTEMPTS NOW:", payment["previous_attempts"])

    recovery_history.append({
        "payment_id": payment["payment_id"],
        "attempt": payment["previous_attempts"],
        "action": "retry",
        "reason": decision["reason"],
        "result": result["result"]
    })

print("\nNEW DECISION:")
print("ACTION:", decision["action"])
print("REASON:", decision["reason"])
print("RETRY AFTER:", decision["retry_after_minutes"], "minutes")

if decision["action"] == "ask_customer":
    message_response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": 
                """
                You are payment recovery assistant. Write a short, polite customer-facing messgae explaining that their payment could not be completed. Do not mention internal rules,retry
attempts, AI or technical details. Keep it under 100 words.
                """
            },
            {
                "role": "user",
                "content": f"""
                Payment: {payment}
                Recovery reason: {decision["reason"]}
                """
            }
        ]
    )
    customer_message = message_response.choices[0].message.content
    print("\nCUSTOMER MESSAGE : ")
    print(customer_message)

current_payment_history = [
    event for event in recovery_history if event["payment_id"] == payment["payment_id"]
]

print("\nRECOVERY HISTORY")
for event in current_payment_history:
    print("ATTEMPT:", event["attempt"])
    print("ACTION:", event["action"])
    print("REASON:", event["reason"])
    print("PAYMENT_ID:", event["payment_id"])
    print("RESULT:",event["result"])

with open("recovery_history.json", "w") as file:
    json.dump(recovery_history, file, indent=4, sort_keys="True")

