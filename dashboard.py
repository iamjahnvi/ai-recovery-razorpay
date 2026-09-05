import streamlit as st
import json

from payment_normalizer import normalize_payment
from recovery_policy import recovery_policy
from recovery_executor import execute_recovery
from risk_engine import calculate_revenue_risk


st.set_page_config(
    page_title="AI Revenue Recovery Agent",
    page_icon="₹",
    layout="wide"
)


st.title("AI Revenue Recovery Agent")
st.caption("Detect revenue at risk → determine intervention → execute bounded recovery")


# Load customer profiles
with open("customer_profiles.json", "r") as file:
    customer_profiles = json.load(file)


# Demo payment
payment_data = {
    "id": "pay_TWrcKJNoyIqcOI",
    "amount": 10000,
    "currency": "INR",
    "status": "failed",
    "method": "netbanking",
    "email": "void@razorpay.com",
    "error_description": (
        "Your payment didn't go through as it was declined by the bank."
    ),
    "error_source": "bank",
    "created_at": 1788285616
}


customer_email = payment_data.get("email")
customer_profile = customer_profiles.get(customer_email)


payment = normalize_payment(
    payment_data,
    customer_profile
)


risk = calculate_revenue_risk(payment)

decision = recovery_policy(payment)

execution = execute_recovery(
    payment,
    decision
)


# Top metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Estimated Revenue at Risk",
        f"₹{risk['revenue_at_risk']:.2f}"
    )

with col2:
    st.metric(
        "Recovery Probability",
        f"{risk['recovery_probability'] * 100:.0f}%"
    )

with col3:
    st.metric(
        "Customer Tier",
        payment["customer_tier"].upper()
    )


st.divider()


# Payment information
st.subheader("Payment Risk")

col1, col2 = st.columns(2)

with col1:
    st.write("**Payment ID:**", payment["payment_id"])
    st.write("**Amount:**", f"₹{payment['amount'] / 100:.2f}")
    st.write("**Method:**", payment["payment_method"])

with col2:
    st.write("**Failure Reason:**", payment["failure_reason"])
    st.write("**Subscription:**", payment["subscription"])
    st.write("**Customer LTV:**", f"₹{payment['lifetime_value']}")


st.divider()


# Agent decision
st.subheader("Agent Decision")

st.write("###", decision["action"].replace("_", " ").upper())

st.write("**Reason:**")
st.write(decision["reason"])

st.write(
    "**Retry After:**",
    f"{decision['retry_after_minutes']} minutes"
)


st.divider()


# Execution
st.subheader("Recovery Execution")

st.write("**Result:**", execution["result"])

st.write("**Message:**", execution["message"])


st.divider()


# Other revenue risk sources
st.subheader("Other Revenue Risk Sources")

col1, col2 = st.columns(2)

with col1:
    st.info(
        "Checkout Abandonment\n\n"
        "Detect abandoned checkout sessions and trigger "
        "customer reminders."
    )

with col2:
    st.warning(
        "Overdue Receivables\n\n"
        "Identify unpaid invoices and trigger payment "
        "collection workflows."
    )


st.divider()

st.caption(
    "AI Revenue Recovery Agent • Razorpay payment events • "
    "Bounded recovery workflow"
)