"""Small placeholder actions module for the WhatsApp scheduler.

Add real WhatsApp integration here; for now the endpoint calls this
function which performs a light-weight action and returns a string.
"""

import logging
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

logger = logging.getLogger(__name__)


def trigger_action():
    """Backward-compatible placeholder used by the earlier UI trigger.

    Kept for compatibility with the simple button that didn't POST phone/body.
    """
    logger.info("whatsapp_scheduler.actions.trigger_action called")
    return "action-triggered"


def send_whatsapp_via_twilio(phone: str, body: str, from_number: str):
    """Send a WhatsApp message via Twilio API when credentials are present.

    Args:
        phone: Recipient phone number (will be prefixed with 'whatsapp:' if needed)
        body: Message body text
        from_number: Twilio WhatsApp number to send from (e.g. 'whatsapp:+1415...')

    Environment variables expected:
      - TWILIO_ACCOUNT_SID
      - TWILIO_AUTH_TOKEN

    Returns Twilio message sid on success. If credentials are not set, this
    function raises an Exception.
    """
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

    if not (account_sid and auth_token):
        raise RuntimeError(
            "Twilio credentials not configured (TWILIO_ACCOUNT_SID/AUTH_TOKEN)"
        )

    if not from_number:
        raise RuntimeError("from_number is required")

    client = Client(account_sid, auth_token)
    # Twilio's WhatsApp API expects 'to' like 'whatsapp:+123456789'
    to = phone if phone.startswith("whatsapp:") else f"whatsapp:{phone}"
    # Ensure from_number has whatsapp: prefix
    from_whatsapp = (
        from_number
        if from_number.startswith("whatsapp:")
        else f"whatsapp:{from_number}"
    )
    message = client.messages.create(body=body, from_=from_whatsapp, to=to)
    logger.info(
        "Sent WhatsApp message sid=%s from=%s to=%s",
        getattr(message, "sid", None),
        from_whatsapp,
        to,
    )
    return getattr(message, "sid", None)
