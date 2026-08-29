from dotenv import load_dotenv
import os
import random 
import json

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
    "insufficient_funds" ,
    "processing_error" ,
    "bank_declined" ,
]

possible_currency = [
    "USD" ,
    "INR",
    "MYR",
    "SGD"
]

possible_customer_tier = [
    "vip",
    "vvip",
    "free",
    "premium",
    "enterprise"
]

possible_card_brand = [
    "Visa" ,
    "Mastercard" ,
    "American Express",
    "RuPay",
    "Diners Club",
    "Discover",
    "Amex"
]

possible_payment_method_type = [   
    "Credit Card" ,
    "Debit Card",
    "UPI" ,
    "Net Banking" ,
    "Digital Wallet" ,
    "EMI" ,
    "Cardless EMI" ,
    "Pay Later" ,
    "Bank Transfer" ,
    "QR Code" ,
    "International Payments" ,
    "Contactless / Tap & Pay",
]

is_subscription = [True,False]


payment = {
    "amount" : random.randint(1000,10000),
    "failure_reason" : random.choice(possible_failure_reasons) ,
    "previous_attempts" : random.randint(1,10),
    "minutes_since_failure" : random.randint(1,60) ,
    "currency" : random.choice(possible_currency) ,
    "customer_tier" : random.choice(possible_customer_tier) ,
    "card_brand" : random.choice(possible_card_brand) ,
    "payment_method" : random.choice(possible_payment_method_type) ,
    "subscription" : random.choice(is_subscription)
}

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
            "reason": f"{failure_reason} cannot be fixed   by retrying - needs updated card details" ,
            "retry_after_minutes": 0,
        }

    if attempts >= 5:
        return {
            "action" : "stop" ,
            "reason" : "Maximun retry attempts exceeded - escalate to write-off/manual review",
            "retry_after_minutes": 0,
        }

    if attempts >=3:
        return{
            "action": "ask_customer",
            "reason":"Multiple automated retries failed-needs customer intervention",
            "retry_after_minutes":0,
        }

    if failure_reason == "insufficient_funds":
        if tier in ("vip", "vvip", "enterprise"):
            return {
                "action": "ask_customer",
                "reason": "High-value customer with insufficient funds — prefer manual outreach over silent retry",
                "retry_after_minutes": 0,
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
            "reason": "Transient failure persisting beyond 30 minutes — likely not self-resolving",
            "retry_after_minutes": 0,
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
        "retry_after_minutes": 0,
    }

response = client.chat.completions.create(
    model="openai/gpt-oss-20b" , 
    messages=[
        {"role":"system" , "content" : """ 
        You are a payment recovery assistant.
        For every failed payment, decide the best recovery action.

        Possible actions :
        -retry
        -ask_customer
        -stop

        Return only valid JSON.
        Do not include markdown , explanations or code fences.

        The JSON must have exactly these keys:
        {
           "action": "retry | ask_customer | stop",
           "reason": "short explaination",
           "retry_after_minutes":0
        }
        """ },

        {"role":"user" , "content": f"Analyse this failed payment and choose the best recovery action: {payment}"}
    ]
)
decision = json.loads(response.choices[0].message.content.lower())

print("AI DECISION : ")
print(decision)

print("AI DECISION:")
print(decision)

print("AI ACTION:", decision["action"])
print("AI REASON:", decision["reason"])
print("RETRY AFTER:", decision["retry_after_minutes"], "minutes")

