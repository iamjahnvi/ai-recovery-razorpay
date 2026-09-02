import os
import razorpay
from dotenv import load_dotenv

load_dotenv()

client = razorpay.Client(
    auth=(
        os.getenv("TEST_API_KEY") ,
        os.getenv("TEST_KEY_SECRET")
    )
)

def fetch_payment(payment_id):
    return client.payment.fetch(payment_id)

