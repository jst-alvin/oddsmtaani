"""Simple MPESA helper supporting Daraja STK Push (sandbox) and simulated payouts.

This module implements token retrieval and STK Push using Safaricom's Daraja
API endpoints (sandbox by default). Payouts (B2C) are simulated unless you
provide production credentials and enable B2C via environment variables.
"""
import base64
import requests
import datetime
import logging
from typing import Optional
from config import (
    MPESA_CONSUMER_KEY,
    MPESA_CONSUMER_SECRET,
    MPESA_PASSKEY,
    MPESA_SHORTCODE,
    CALLBACK_URL,
    USE_MPESA,
)

logger = logging.getLogger(__name__)

# Default to sandbox endpoints; override by setting MPESA_BASE_URL environment
# variable in `config.py` if you need production.
MPESA_BASE = "https://sandbox.safaricom.co.ke"


def get_access_token() -> Optional[str]:
    """Retrieve OAuth access token from Daraja sandbox.

    Returns the access token string or None if retrieval failed.
    """
    if not (MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET):
        logger.debug("MPESA consumer credentials not configured")
        return None
    url = f"{MPESA_BASE}/oauth/v1/generate?grant_type=client_credentials"
    auth = (MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET)
    try:
        r = requests.get(url, auth=auth, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data.get("access_token")
    except Exception as e:
        logger.exception("Failed to retrieve MPESA access token: %s", e)
        return None


def _timestamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


def stk_push(phone: str, amount: int, account_reference: str = "OddsMtaani", callback_url: str = CALLBACK_URL) -> Optional[str]:
    """Initiate STK Push to the given phone number.

    Returns the CheckoutRequestID (string) on success, or None on failure.
    """
    # Log the configuration status
    logger.info("=== STK Push Debug Info ===")
    logger.info(f"MPESA_CONSUMER_KEY present: {bool(MPESA_CONSUMER_KEY)}")
    logger.info(f"MPESA_CONSUMER_SECRET present: {bool(MPESA_CONSUMER_SECRET)}")
    logger.info(f"MPESA_PASSKEY: {MPESA_PASSKEY}")
    logger.info(f"MPESA_SHORTCODE: {MPESA_SHORTCODE}")
    logger.info(f"CALLBACK_URL: {callback_url}")
    logger.info(f"Phone: {phone}, Amount: {amount}")
    
    # If passkey is not set (still "YOUR_PASSKEY"), use simulated flow
    if MPESA_PASSKEY == "YOUR_PASSKEY" or not MPESA_PASSKEY:
        logger.info("MPESA Passkey not configured. Simulating STK Push...")
        # Simulate successful STK Push
        checkout_id = f"SIMULATED-{phone}-{amount}"
        with open("simulated_stk_push.log", "a", encoding="utf-8") as f:
            f.write(f"STK Push SIMULATED: Phone={phone} Amount={amount} CheckoutID={checkout_id}\n")
        logger.info(f"Simulated STK Push result: {checkout_id}")
        return checkout_id
    
    token = get_access_token()
    if not token:
        logger.error("Failed to get access token - check consumer key/secret")
        return None

    timestamp = _timestamp()
    password = base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()).decode()
    url = f"{MPESA_BASE}/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": callback_url,
        "AccountReference": account_reference,
        "TransactionDesc": "Payment for OddsMtaani",
    }

    try:
        logger.info(f"Sending STK Push request to {url}")
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        logger.info(f"Response status: {r.status_code}")
        logger.info(f"Response body: {r.text}")
        r.raise_for_status()
        data = r.json()
        # On success, Daraja returns CheckoutRequestID inside response
        checkout_id = data.get("CheckoutRequestID") or data.get("ResponseDescription")
        logger.info("STK Push initiated: %s", data)
        return checkout_id
    except Exception as e:
        logger.exception("STK Push failed: %s", e)
        return None


def send_payout(phone: str, amount: int) -> str:
    """Send payout to a user.

    NOTE: B2C payouts require special credentials and account setup with
    Safaricom. By default this function simulates the payout and logs it.
    If you set the appropriate credentials and endpoints you can extend this
    function to call the real B2C API.
    """
    if not USE_MPESA:
        logger.info("Simulating payout of KES %s to %s", amount, phone)
        # append to a local log file for traceability
        with open("simulated_payouts.log", "a", encoding="utf-8") as f:
            f.write(f"PAYOUT SIMULATED: To={phone} Amount={amount}\n")
        return "SIMULATED"

    # If USE_MPESA is True, but real B2C not implemented, fallback to simulated
    logger.warning("MPESA configured but B2C payout not implemented; simulating")
    with open("simulated_payouts.log", "a", encoding="utf-8") as f:
        f.write(f"PAYOUT (SIMULATED FALLBACK): To={phone} Amount={amount}\n")
    return "SIMULATED"
