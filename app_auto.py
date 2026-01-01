"""Automatic M-Pesa STK Push - User gets PIN prompt on their phone!"""
from flask import Flask, render_template, request, jsonify
import logging
from datetime import datetime
import requests
import base64
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Configuration
ENTRY_FEE = 50

# Daraja API credentials (using sandbox)
CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY', '0NAF8Gv2pDLdkzwdHn9y7IyZYXKjAq5fmIuTK23DpKQBe2A5')
CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET', 'J4uschSQH7lv8IEdEiPDf4l5dnCAhRXtjAMS01b6uC1GcssfCjQFDf8h9Z9A1B0B')
SHORTCODE = '174379'  # Sandbox shortcode
PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a5a2c09b3dcb6c2f6ceda15e3b8b8e38c8d9e1'  # Sandbox passkey
CALLBACK_URL = 'https://yourdomain.com/callback'  # Not needed for sandbox testing

# Store payments
payments = {}


def get_access_token():
    """Get Daraja API access token"""
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    try:
        r = requests.get(url, auth=(CONSUMER_KEY, CONSUMER_SECRET), timeout=10)
        r.raise_for_status()
        return r.json().get('access_token')
    except Exception as e:
        logging.error(f"Token error: {e}")
        return None


def send_stk_push(phone, amount):
    """Send STK Push to user's phone"""
    token = get_access_token()
    if not token:
        return {'success': False, 'message': 'Failed to connect to M-Pesa'}
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f"{SHORTCODE}{PASSKEY}{timestamp}".encode()).decode()
    
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "OddsMtaani",
        "TransactionDesc": f"Payment for OddsMtaani - KES {amount}"
    }
    
    try:
        logging.info(f"Sending STK Push to {phone}")
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        logging.info(f"Response: {r.status_code} - {r.text}")
        r.raise_for_status()
        data = r.json()
        
        if data.get('ResponseCode') == '0':
            checkout_id = data.get('CheckoutRequestID')
            return {
                'success': True,
                'checkout_id': checkout_id,
                'message': 'Check your phone for M-Pesa prompt!'
            }
        else:
            return {
                'success': False,
                'message': data.get('ResponseDescription', 'STK Push failed')
            }
    except Exception as e:
        logging.exception(f"STK Push error: {e}")
        return {'success': False, 'message': f'Error: {str(e)}'}


@app.route('/')
def index():
    return render_template('stk_push.html', entry_fee=ENTRY_FEE)


@app.route('/pay', methods=['POST'])
def pay():
    phone = request.form.get('phone')
    
    if not phone:
        return render_template('result.html', message='❌ Phone number required')
    
    # Clean phone number
    phone = phone.strip().replace(' ', '')
    if not phone.startswith('254'):
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('+'):
            phone = phone[1:]
    
    # Send STK Push
    result = send_stk_push(phone, ENTRY_FEE)
    
    if result['success']:
        checkout_id = result['checkout_id']
        payments[checkout_id] = {
            'phone': phone,
            'amount': ENTRY_FEE,
            'status': 'PENDING',
            'timestamp': datetime.now().isoformat()
        }
        
        return render_template('result.html', 
                             message=f"✅ {result['message']}<br><br>📱 Check your phone and enter your M-Pesa PIN to complete payment.<br><br><small>Reference: {checkout_id}</small>")
    else:
        return render_template('result.html', 
                             message=f"❌ {result['message']}<br><br>Please try again or contact support.")


@app.route('/callback', methods=['POST'])
def callback():
    """Receive M-Pesa callback (for production use)"""
    data = request.get_json(force=True)
    logging.info(f"Callback received: {data}")
    return jsonify({'ResultCode': 0, 'ResultDesc': 'Accepted'})


@app.route('/admin')
def admin():
    """Simple admin view"""
    return render_template('admin_simple.html', payments=payments, entry_fee=ENTRY_FEE)


if __name__ == '__main__':
    print(f"\n{'='*60}")
    print(f"🚀 OddsMtaani - Automatic M-Pesa STK Push")
    print(f"{'='*60}")
    print(f"💰 Entry Fee: KES {ENTRY_FEE}")
    print(f"📱 Users will get PIN prompt on their phone automatically!")
    print(f"\n🌐 Open: http://127.0.0.1:5000")
    print(f"{'='*60}\n")
    app.run(port=5000, debug=True)
