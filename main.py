from dotenv import load_dotenv
import os
import random 

load_dotenv()
# python, go inside .env and load the secrets.

from openai import OpenAI
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"), 
    base_url="https://api.groq.com/openai/v1"
)

possible_failure_reasons = [
    "incorrect_CVC"
    "mistyped_card_number",
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
    "Credit Card"
    "Debit Card"
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

def recovery_policy(payment):
    if payment["previous_attempts"] >= 3:
        return "ask_customer"

    if payment["failure_reason"] == "insufficient_funds":
        return "ask_customer"

    if payment["failure_reason"] == "bank_declined":
        return "retry"

    if payment["minutes_since_failure"] <= 5:
        return "retry"

    return "stop"

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

        Return your answer in this format :
        action : <action> 
        reason : <short answer>
        retry_after_minutes : <number, use 0 if not applicable>
        """ },

        {"role":"user" , "content": f"Analyse this failed payment and choose the best recovery action: {payment}"}
    ]
)
decision = response.choices[0].message.content.lower()

print("AI DECISION : ")
print(decision)

if "ask_customer" in decision :
    print("Recovery system will contact the customer.")

elif "stop" in decision :
    print("Recovery system will stop further attempts.")

elif "retry" in decision :
    print("Recovery system will return the payment")

else :
    print("Unknown action.")

print("Final action :", recovery_policy(payment))

