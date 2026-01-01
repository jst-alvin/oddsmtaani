# Box Game — MPESA & SMS demo

This small demo shows how to:

- Request payment using Safaricom Daraja STK Push (M-Pesa sandbox)
- Send SMS via Twilio, with a simulated fallback if Twilio isn't configured

Files added:

- `app.py` — Flask web app with payment form and payout admin endpoint
- `mpesa.py` — MPESA helper (token retrieval, STK Push, simulated payout)
- `sms.py` — SMS helper with Twilio optional and simulated fallback
- `.env.example` — example environment variables
- `requirements.txt` — dependencies

Setup

1. Create a virtual environment and activate it (Windows cmd):

```cmd
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```cmd
python -m pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in values (or set environment variables).

4. Run the Flask app:

```cmd
python app.py
```

5. Open http://127.0.0.1:5000 in your browser.

Notes

- Storing secrets in `.env` is convenient for development but avoid committing
  real credentials to source control.
- Daraja callbacks require a public HTTPS endpoint; use `ngrok` or similar for
  local development and set `CALLBACK_URL` accordingly.
- B2C payouts are simulated in this demo. To implement real payouts you need
  production-level credentials and to follow Safaricom's B2C API requirements.
