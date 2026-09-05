import json
import os
import hmac
import hashlib
import urllib.request

from dotenv import load_dotenv


load_dotenv()

WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

URL = "http://127.0.0.1:8000/webhook/payment-failed"


payload = {
    "event": "payment.failed",
    "payload": {
        "payment": {
            "entity": {
                "id": "pay_WEBHOOK_TEST_001",
                "amount": 10000,
                "currency": "INR",
                "status": "failed",
                "method": "netbanking",
                "email": "void@razorpay.com",
                "error_description": "Your payment didn't go through as it was declined by the bank.",
                "error_source": "bank",
                "created_at": 1788285616
            }
        }
    }
}


raw_body = json.dumps(
    payload,
    separators=(",", ":")
).encode("utf-8")


signature = hmac.new(
    WEBHOOK_SECRET.encode(),
    raw_body,
    hashlib.sha256
).hexdigest()


request = urllib.request.Request(
    URL,
    data=raw_body,
    headers={
        "Content-Type": "application/json",
        "X-Razorpay-Signature": signature,
        "X-Razorpay-Event-Id": "evt_WEBHOOK_TEST_002"
    },
    method="POST"
)


try:

    with urllib.request.urlopen(request) as response:

        print("\nSTATUS:", response.status)
        print("RESPONSE:")
        print(response.read().decode())

except urllib.error.HTTPError as error:

    print("\nSTATUS:", error.code)
    print("RESPONSE:")
    print(error.read().decode())