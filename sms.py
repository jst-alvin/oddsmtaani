"""SMS helper with optional Twilio usage and a simulated fallback."""
from typing import Optional
import logging
from config import ENTRY_FEE, TWILIO_SID, TWILIO_TOKEN, TWILIO_NUMBER, USE_TWILIO

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

try:
    from twilio.rest import Client
except Exception:
    Client = None

_twilio_client = None
if USE_TWILIO and Client:
    _twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)


def send_game_sms(phone: str, use_twilio: Optional[bool] = None) -> str:
    """Send the game SMS.

    If `use_twilio` is True and Twilio is configured, attempt to send via
    Twilio. If Twilio is not available (or `use_twilio` is False), the
    function will simulate sending by printing and writing to
    `simulated_sms.log`.

    Returns the Twilio message SID if sent, or the string 'SIMULATED'.
    """
    body = f"⚡ OddsMtaani\nPay KES {ENTRY_FEE} to play.\nProceed after payment."

    if use_twilio is None:
        use_twilio = bool(_twilio_client)

    if use_twilio:
        if not _twilio_client:
            raise RuntimeError("Twilio client not initialized. Check credentials and install 'twilio'.")
        msg = _twilio_client.messages.create(body=body, from_=TWILIO_NUMBER, to=phone)
        logger.info("Sent SMS via Twilio to %s (sid=%s)", phone, getattr(msg, 'sid', None))
        return getattr(msg, 'sid', 'UNKNOWN')

    # Fallback: simulate send
    logger.info("Simulating SMS to %s", phone)
    print("----- SIMULATED SMS -----")
    print(f"To: {phone}")
    print(body)
    print("-------------------------")
    with open("simulated_sms.log", "a", encoding="utf-8") as f:
        f.write(f"To: {phone}\n{body}\n---\n")
    return "SIMULATED"

