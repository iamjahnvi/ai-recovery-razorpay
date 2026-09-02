# for testing the connection
# This is the Razorpay communication layer.
# Its job is basically:
# "Give me a Razorpay Payment ID, I'll call Razorpay's API and bring back the actual payment data."

from payment_normalizer import normalize_payment
from razorpay_client import fetch_payment
from razorpay_client import client
from payment_mapper import map_razorpay_payment
from recovery_policy import recovery_policy

payment_id = input("Enter Razorpay payment ID: ")

payment_data = client.payment.fetch(payment_id)

payment = map_razorpay_payment(payment_data)

print("\nPAYMENT FOR RECOVERY ENGINE:")
print(payment)

decision = recovery_policy(payment)

print("\nRECOVERY DECISION:")
print("ACTION:", decision["action"])
print("REASON:", decision["reason"])
print("RETRY AFTER:", decision["retry_after_minutes"])

normalized_payment = normalize_payment(payment_data)

print("\nNORMALIZED PAYMENT:")
print(normalized_payment)

