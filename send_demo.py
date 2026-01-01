"""Small CLI to demo sending an SMS (real via Twilio if configured, else simulated)."""
from sms import send_game_sms


def main():
    phone = input("Enter phone number (e.g. +2547...): ").strip()
    choice = input("Send using Twilio if available? (y/N): ").strip().lower()
    use_twilio = True if choice == 'y' else False
    try:
        sid = send_game_sms(phone, use_twilio=use_twilio)
        print("Result:", sid)
    except Exception as e:
        print("Error sending SMS:", e)


if __name__ == '__main__':
    main()
