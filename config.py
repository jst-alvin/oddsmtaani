"""Project configuration.

This module reads configuration values from environment variables. It will
attempt to load a local `.env` file if `python-dotenv` is installed. Keep
secrets out of source control — set them in environment variables or a
secrets manager.
"""
from pathlib import Path
import os

try:
	# optional dependency: if present, load a .env file
	from dotenv import load_dotenv
	env_path = Path(__file__).with_suffix('.env')
	if env_path.exists():
		load_dotenv(env_path)
	else:
		load_dotenv()
except Exception:
	# dotenv not installed or failed — environment variables will be used
	pass


def _get_env(key: str, default: str | None = None) -> str | None:
	return os.getenv(key, default)


ENTRY_FEE = int(_get_env("ENTRY_FEE", "50"))

# Payment phone number
PAYMENT_NUMBER = _get_env("PAYMENT_NUMBER", "0768933271")

# Twilio settings (leave empty or unset to disable Twilio usage)
TWILIO_SID = _get_env("TWILIO_SID")
TWILIO_TOKEN = _get_env("TWILIO_TOKEN")
TWILIO_NUMBER = _get_env("TWILIO_NUMBER")

# M-Pesa settings (optional)
MPESA_SHORTCODE = _get_env("MPESA_SHORTCODE")
MPESA_PASSKEY = _get_env("MPESA_PASSKEY")
MPESA_CONSUMER_KEY = _get_env("MPESA_CONSUMER_KEY")
MPESA_CONSUMER_SECRET = _get_env("MPESA_CONSUMER_SECRET")
CALLBACK_URL = _get_env("CALLBACK_URL")

# Convenience booleans
USE_TWILIO = bool(TWILIO_SID and TWILIO_TOKEN and TWILIO_NUMBER)
USE_MPESA = bool(MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET and MPESA_PASSKEY)
