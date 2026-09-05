# AI Revenue Recovery Agent

An AI-powered revenue recovery agent that detects revenue at risk, determines the appropriate recovery intervention, executes bounded actions, and maintains an auditable recovery trail.

Built for the Razorpay AI Buildathon — Track 3: Revenue Recovery.

## Problem

Businesses lose revenue through:

- Failed payments
- Checkout abandonment
- Subscription payment failures
- Overdue receivables

Traditional systems often stop at detecting the failure. They don't determine the appropriate next action or measure recovery across a batch.

## Solution

This project implements an automated recovery pipeline:

Detection → Risk Assessment → Decision → Execution → Recovery → Audit

The agent:

1. Detects revenue-at-risk events.
2. Normalizes payment and customer data.
3. Estimates recoverable revenue.
4. Determines the appropriate intervention using recovery policies.
5. Executes only bounded, predefined actions.
6. Stops or escalates when recovery should not continue.
7. Tracks outcomes and recovery metrics.
8. Maintains an audit trail and prevents duplicate event processing.

## Architecture

```text
Razorpay Payment / Webhook
          ↓
   Event Detection
          ↓
   Payment Normalizer
          ↓
     Risk Engine
          ↓
 Recovery Policy Engine
          ↓
  Bounded Execution Layer
          ↓
 Recovery / Escalation
          ↓
 Audit Logger + Metrics
          ↓
      Dashboard

## Supported Recovery Scenarios

### Payment Failure

The agent analyzes:

- Failure reason
- Previous attempts
- Time since failure
- Customer tier
- Subscription status

Possible actions:

- Retry
- Ask customer
- Stop and escalate

### Checkout Abandonment

Detects abandoned checkouts and schedules a recovery reminder.

### Overdue Receivables

Calculates days overdue and schedules a payment collection reminder.

### Subscription Failure

Prioritizes recovery of failed recurring payments while respecting retry limits.

## Risk Engine

The system estimates:

Revenue at Risk = Payment Amount × Recovery Probability

Recovery probability is adjusted based on failure reason and customer value.

## Bounded Agent Execution

The agent does not blindly retry payments.

It follows explicit stopping rules:

- Non-retryable failures → customer intervention
- Multiple failed attempts → escalation
- Maximum retry threshold → stop
- Persistent transient failures → customer intervention
- Unknown scenarios → safe stop/manual review

The execution layer is sandboxed and does not charge real customers.

## Webhook Integration

The system exposes a FastAPI webhook endpoint for Razorpay `payment.failed` events.

Webhook processing includes:

- HMAC SHA-256 signature verification
- Event ID validation
- Idempotent event processing
- Payment normalization
- Risk assessment
- Recovery decision
- Bounded execution
- Audit logging

## Batch Processing

The agent can process multiple revenue-at-risk events and calculate:

- Total revenue at risk
- Recovered revenue
- Recovery rate
- Recovered events
- Escalated events
- Stopped events

Example sandbox run:

Revenue at risk: ₹64,160  
Recovered revenue: ₹1,700  
Recovery rate: 2.65%  
Events processed: 7  
Recovered events: 4  
Escalated: 2  
Stopped: 0

> These figures are generated from sandbox/demo outcomes and do not represent real customer revenue.

## Dashboard

A Streamlit dashboard provides visibility into:

- Revenue at risk
- Recovered revenue
- Recovery rate
- Event outcomes
- Recovery decisions
- Audit information

## Tech Stack

- Python
- FastAPI
- Streamlit
- Razorpay APIs & Webhooks
- Groq / OpenAI-compatible API
- JSON-based event and audit storage
- HMAC SHA-256
- Uvicorn

## Project Structure

```text
ai-recovery/
│
├── main.py
├── webhook_server.py
├── batch_processor.py
├── recovery_policy.py
├── recovery_executor.py
├── payment_normalizer.py
├── risk_engine.py
├── event_processor.py
├── recovery_metrics.py
├── audit_logger.py
├── batch_audit.py
├── agent_summary.py
├── idempotency.py
├── dashboard.py
│
├── customer_profiles.json
├── batch_events.json
│
├── requirements.txt
├── .gitignore
└── README.md      

## Running Locally

### 1.Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies

```powershell
pip install -r requirements.txt
```

Create a .env file containing the required API credentials.

Run the main recovery flow:

```powershell
python main.py
```


Run batch processing:

```powershell
python batch_processing.py
```

Generate the agent summary:

```powershell
python agent_summary.py
```

Run the FastAPI webhook server

```powershell
uvicorn webhook_server:app --reload
```

Run the dashboard:
```powershell
streamlit run dashboard.py
```

## Security

- API credentials are stored in environment variables.
- `.env` is excluded from version control.
- Webhook requests are verified using HMAC SHA-256.
- Duplicate webhook events are prevented using event IDs and idempotency checks.
- The project operates in Razorpay Test Mode and does not charge real customers.

## Future Improvements

- Production-grade database-backed event storage
- More advanced recovery prediction models
- Adaptive retry scheduling
- Customer communication channels
- Additional payment-provider integrations
- Advanced revenue recovery analytics
- Production workflow orchestration

## License

Built as a hackathon prototype for demonstrating AI-driven revenue recovery workflows.