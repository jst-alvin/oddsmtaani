"""Flutterwave payment integration - simpler alternative to MPESA.

Flutterwave supports M-Pesa, cards, mobile money, and more.
Get your API keys from https://dashboard.flutterwave.com/
"""
import requests
import logging
from typing import Optional
from config import ENTRY_FEE
import os

logger = logging.getLogger(__name__)

# Get from environment
FLW_PUBLIC_KEY = os.getenv('FLW_PUBLIC_KEY', '')
FLW_SECRET_KEY = os.getenv('FLW_SECRET_KEY', '')
FLW_ENCRYPTION_KEY = os.getenv('FLW_ENCRYPTION_KEY', '')


def create_payment(phone: str, email: str, amount: int = ENTRY_FEE) -> dict:
    """Create a Flutterwave payment.
    
    Returns dict with:
    - link: Payment URL to redirect user to
    - tx_ref: Transaction reference
    - simulated: True if simulated
    """
    # If no keys configured, simulate
    if not FLW_SECRET_KEY or not FLW_PUBLIC_KEY:
        logger.info("Flutterwave not configured. Simulating payment...")
        tx_ref = f"SIM-{phone}-{amount}"
        with open("simulated_payments.log", "a", encoding="utf-8") as f:
            f.write(f"Payment SIMULATED: Phone={phone} Email={email} Amount={amount} TxRef={tx_ref}\n")
        return {
            'simulated': True,
            'tx_ref': tx_ref,
            'link': None,
            'message': f'Payment simulated successfully! Ref: {tx_ref}'
        }
    
    # Real Flutterwave payment
    url = "https://api.flutterwave.com/v3/payments"
    tx_ref = f"ODM-{phone}-{amount}"
    
    payload = {
        "tx_ref": tx_ref,
        "amount": str(amount),
        "currency": "KES",
        "redirect_url": "http://127.0.0.1:5000/payment/callback",
        "payment_options": "mpesa,card,mobilemoney",
        "customer": {
            "email": email,
            "phonenumber": phone,
            "name": "OddsMtaani User"
        },
        "customizations": {
            "title": "OddsMtaani Payment",
            "description": f"Entry fee payment - KES {amount}",
            "logo": "https://via.placeholder.com/150"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {FLW_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        logger.info(f"Creating Flutterwave payment for {phone}")
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        logger.info(f"Flutterwave response status: {r.status_code}")
        logger.info(f"Flutterwave response: {r.text}")
        r.raise_for_status()
        data = r.json()
        
        if data.get('status') == 'success':
            return {
                'simulated': False,
                'tx_ref': tx_ref,
                'link': data['data']['link'],
                'message': 'Payment initiated successfully!'
            }
        else:
            logger.error(f"Flutterwave error: {data}")
            return {'simulated': False, 'tx_ref': None, 'link': None, 'message': 'Payment failed'}
    except Exception as e:
        logger.exception(f"Flutterwave payment failed: {e}")
        return {'simulated': False, 'tx_ref': None, 'link': None, 'message': f'Error: {e}'}


def verify_payment(tx_ref: str) -> bool:
    """Verify a payment was completed."""
    if tx_ref.startswith('SIM-'):
        logger.info(f"Simulated payment {tx_ref} - auto verified")
        return True
    
    if not FLW_SECRET_KEY:
        return False
    
    url = f"https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={tx_ref}"
    headers = {"Authorization": f"Bearer {FLW_SECRET_KEY}"}
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        status = data.get('data', {}).get('status')
        return status == 'successful'
    except Exception as e:
        logger.exception(f"Payment verification failed: {e}")
        return False
