from dotenv import load_dotenv
import os
import json

from recovery_policy import recovery_policy
from recovery_stimulator import stimulate_retry
from payment_normalizer import normalize_payment

import razorpay

load_dotenv()
# python, go inside .env and load the secrets.
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

razorpay_client = razorpay.Client(
    auth=(
        os.getenv("TEST_API_KEY"),
        os.getenv("TEST_KEY_SECRET")
    )
)

payment_id = input("Enter Razorpay payment ID: ")

razorpay_payment = razorpay_client.payment.fetch(payment_id)

payment = normalize_payment(razorpay_payment)

print("\nPAYMENT FOR RECOVERY ENGINE:")
print(payment)

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
    event 
    for event in recovery_history if event["payment_id"] == payment["payment_id"]
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

