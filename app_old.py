from flask import Flask, render_template, request, redirect, url_for, jsonify
import logging
from config import ENTRY_FEE
import sms
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Simple in-memory store for payments
payments = {}
payment_counter = 1


@app.route('/')
def index():
    return render_template('payment_page.html', 
                         entry_fee=config.ENTRY_FEE,
                         payment_number=config.PAYMENT_NUMBER)


@app.route('/pay', methods=['POST'])
def pay():
    phone = request.form.get('phone')
    print(f"\n=== PAY ROUTE CALLED ===")
    print(f"Phone: {phone}")
    if not phone:
        return redirect(url_for('index'))
    # start STK push with error handling to surface issues to the UI
    print(f"Calling mpesa.stk_push with phone={phone}, amount={ENTRY_FEE}")
    try:
        checkout = mpesa.stk_push(phone, ENTRY_FEE)
        print(f"stk_push returned: {checkout}")
    except Exception as e:
        print(f"Exception during STK Push: {e}")
        logging.exception('Error during STK Push')
        return render_template('result.html', message=f'Error initiating STK Push: {e}')

    if checkout:
        payments[checkout] = {'phone': phone, 'status': 'PENDING'}
        return render_template('result.html', message=f'STK Push initiated (id={checkout}). Check your phone.')
    else:
        print("Checkout is None - falling back to simulated flow")
        return render_template('result.html', message='Failed to initiate STK Push. Falling back to simulated flow.' )


@app.route('/payment/callback')
def payment_callback():
    """Flutterwave redirects here after payment."""
    status = request.args.get('status')
    tx_ref = request.args.get('tx_ref')
    
    if status == 'successful' and tx_ref:
        # Verify the payment
        verified = flutterwave_pay.verify_payment(tx_ref)
        if verified:
            if tx_ref in payments:
                payments[tx_ref]['status'] = 'SUCCESS'
            return render_template('result.html', message=f'✅ Payment successful! Reference: {tx_ref}')
        else:
            return render_template('result.html', message='⚠️ Payment verification failed')
    else:
        return render_template('result.html', message='❌ Payment cancelled or failed')


@app.route('/payout', methods=['POST'])
def payout():
    # Admin endpoint to payout a winner (simulated for now)
    phone = request.form.get('phone')
    amount = request.form.get('amount')
    if not phone or not amount:
        return render_template('result.html', message='Phone and amount required')
    try:
        amount = int(amount)
    except Exception:
        return render_template('result.html', message='Invalid amount')

    # Simulate payout
    logging.info(f"Simulating payout of KES {amount} to {phone}")
    with open("simulated_payouts.log", "a", encoding="utf-8") as f:
        f.write(f"PAYOUT: To={phone} Amount={amount}\n")
    return render_template('result.html', message=f'Payout simulated: KES {amount} to {phone}')


if __name__ == '__main__':
    app.run(port=5000, debug=True)

