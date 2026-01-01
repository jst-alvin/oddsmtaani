from flask import Flask, render_template, request, jsonify, session
import config
print("[DEBUG] Loaded config from", getattr(config, '__file__', None))
print("[DEBUG] PAYMENT_NUMBER", getattr(config, 'PAYMENT_NUMBER', None))
print("[DEBUG] ENTRY_FEE", getattr(config, 'ENTRY_FEE', None))
import logging
from datetime import datetime
import secrets
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
logging.basicConfig(level=logging.INFO)

# In-memory storage (use database in production)
pending_payments = {}  # {payment_id: {phone, amount, timestamp, status}}
confirmed_payments = {}  # {payment_id: {phone, amount, confirmed_at}}


@app.route('/')
def index():
    return render_template('payment_page.html', 
                         entry_fee=config.ENTRY_FEE,
                         payment_number=config.PAYMENT_NUMBER)


@app.route('/pay', methods=['POST'])
def pay():
    phone = request.form.get('phone')
    
    if not phone:
        return render_template('result.html', 
                             success=False, 
                             message="Phone number is required")
    
    # Generate unique payment ID
    payment_id = f"PAY{datetime.now().strftime('%Y%m%d%H%M%S')}{secrets.token_hex(3).upper()}"
    
    # Store pending payment
    pending_payments[payment_id] = {
        'phone': phone,
        'amount': config.ENTRY_FEE,
        'timestamp': datetime.now().isoformat(),
        'status': 'pending'
    }
    
    # Save to session for user to check status
    session['payment_id'] = payment_id
    
    logging.info(f"New payment created: {payment_id} for {phone}")
    
    return render_template('payment_instructions.html',
                         payment_id=payment_id,
                         amount=config.ENTRY_FEE,
                         payment_number=config.PAYMENT_NUMBER,
                         phone=phone)


@app.route('/check-status')
def check_status():
    payment_id = session.get('payment_id')
    
    if not payment_id:
        return render_template('result.html',
                             success=False,
                             message="No payment found. Please start a new payment.")
    
    # Check if payment is confirmed
    if payment_id in confirmed_payments:
        return render_template('box_game.html',
                             payment_id=payment_id,
                             phone=confirmed_payments[payment_id]['phone'])
    
    # Check if payment is still pending
    if payment_id in pending_payments:
        return render_template('result.html',
                             success=False,
                             message=f"Payment {payment_id} is still pending verification. Please wait for confirmation or contact admin.")
    
    return render_template('result.html',
                         success=False,
                         message="Payment not found.")


@app.route('/admin')
def admin():
    return render_template('admin_dashboard.html',
                         pending=pending_payments,
                         confirmed=confirmed_payments,
                         payment_number=config.PAYMENT_NUMBER)


@app.route('/admin/confirm/<payment_id>', methods=['POST'])
def confirm_payment(payment_id):
    if payment_id in pending_payments:
        payment = pending_payments.pop(payment_id)
        payment['confirmed_at'] = datetime.now().isoformat()
        confirmed_payments[payment_id] = payment
        
        logging.info(f"✅ Payment {payment_id} confirmed for {payment['phone']}")
        
        return jsonify({
            'success': True,
            'message': f'Payment {payment_id} confirmed'
        })
    
    return jsonify({
        'success': False,
        'message': 'Payment not found'
    }), 404


@app.route('/admin/reject/<payment_id>', methods=['POST'])
def reject_payment(payment_id):
    if payment_id in pending_payments:
        payment = pending_payments.pop(payment_id)
        
        logging.info(f"❌ Payment {payment_id} rejected for {payment['phone']}")
        
        return jsonify({
            'success': True,
            'message': f'Payment {payment_id} rejected'
        })
    
    return jsonify({
        'success': False,
        'message': 'Payment not found'
    }), 404


@app.route('/game-result', methods=['POST'])
def game_result():
    data = request.get_json()
    payment_id = data.get('payment_id')
    prize = data.get('prize')
    
    if payment_id and prize:
        # Log the game result
        logging.info(f"🎮 Game result for {payment_id}: Prize KES {prize}")
        
        # Store in confirmed_payments for record-keeping
        if payment_id in confirmed_payments:
            confirmed_payments[payment_id]['prize'] = prize
        
        return jsonify({'success': True, 'message': 'Result logged'})
    
    return jsonify({'success': False, 'message': 'Invalid data'}), 400


if __name__ == '__main__':
    app.run(port=5000, debug=True)

