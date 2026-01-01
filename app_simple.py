"""Simple direct payment system for OddsMtaani - No API needed!"""
from flask import Flask, render_template, request, jsonify
import logging
from datetime import datetime
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Configuration
ENTRY_FEE = 50
PAYMENT_NUMBER = os.getenv('PAYMENT_NUMBER', '+254700000000')  # Your M-Pesa number

# Store payments in memory
payments = {}
payment_counter = 1


@app.route('/')
def index():
    return render_template('index_simple.html', 
                         entry_fee=ENTRY_FEE, 
                         payment_number=PAYMENT_NUMBER)


@app.route('/pay', methods=['POST'])
def pay():
    global payment_counter
    phone = request.form.get('phone')
    
    if not phone:
        return render_template('result.html', message='❌ Phone number required')
    
    # Create payment request
    payment_id = f"ODM{payment_counter:04d}"
    payment_counter += 1
    
    payments[payment_id] = {
        'phone': phone,
        'amount': ENTRY_FEE,
        'status': 'PENDING',
        'timestamp': datetime.now().isoformat()
    }
    
    # Log for your reference
    with open("pending_payments.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | ID: {payment_id} | Phone: {phone} | Amount: KES {ENTRY_FEE} | Status: PENDING\n")
    
    return render_template('payment_instructions.html', 
                         payment_id=payment_id, 
                         phone=phone, 
                         amount=ENTRY_FEE,
                         payment_number=PAYMENT_NUMBER)


@app.route('/admin')
def admin():
    """Admin page to view and confirm payments"""
    pending = {k: v for k, v in payments.items() if v['status'] == 'PENDING'}
    confirmed = {k: v for k, v in payments.items() if v['status'] == 'CONFIRMED'}
    return render_template('admin.html', pending=pending, confirmed=confirmed, entry_fee=ENTRY_FEE)


@app.route('/admin/confirm/<payment_id>', methods=['POST'])
def confirm_payment(payment_id):
    """Confirm a payment was received"""
    if payment_id in payments:
        payments[payment_id]['status'] = 'CONFIRMED'
        payments[payment_id]['confirmed_at'] = datetime.now().isoformat()
        
        # Log confirmation
        with open("confirmed_payments.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} | ID: {payment_id} | Phone: {payments[payment_id]['phone']} | CONFIRMED\n")
        
        return jsonify({'success': True, 'message': 'Payment confirmed'})
    return jsonify({'success': False, 'message': 'Payment not found'})


@app.route('/payout', methods=['POST'])
def payout():
    """Record payout to winner"""
    phone = request.form.get('phone')
    amount = request.form.get('amount')
    
    if not phone or not amount:
        return render_template('result.html', message='❌ Phone and amount required')
    
    try:
        amount = int(amount)
    except:
        return render_template('result.html', message='❌ Invalid amount')
    
    # Log payout
    with open("payouts.log", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | To: {phone} | Amount: KES {amount} | SENT\n")
    
    return render_template('result.html', 
                         message=f'✅ Payout recorded: KES {amount} to {phone}. Send via M-Pesa now!')


if __name__ == '__main__':
    print(f"\n{'='*60}")
    print(f"🚀 OddsMtaani Payment System Starting...")
    print(f"{'='*60}")
    print(f"💰 Entry Fee: KES {ENTRY_FEE}")
    print(f"📱 Your Payment Number: {PAYMENT_NUMBER}")
    print(f"\n📋 User Page: http://127.0.0.1:5000")
    print(f"🔐 Admin Page: http://127.0.0.1:5000/admin")
    print(f"{'='*60}\n")
    app.run(port=5000, debug=True)
