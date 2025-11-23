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
    logger.info('whatsapp_scheduler.actions.trigger_action called')
    return 'action-triggered'


def send_whatsapp_via_twilio(phone: str, body: str):
    """Send a WhatsApp message via Twilio API when credentials are present.

    Environment variables expected:
      - TWILIO_ACCOUNT_SID
      - TWILIO_AUTH_TOKEN
      - TWILIO_WHATSAPP_FROM  (e.g. 'whatsapp:+1415...')

    Returns Twilio message sid on success. If credentials are not set, this
    function raises an Exception.
    """
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_whatsapp = os.environ.get('TWILIO_WHATSAPP_FROM')

    if not (account_sid and auth_token and from_whatsapp):
        raise RuntimeError('Twilio credentials not configured (TWILIO_ACCOUNT_SID/AUTH_TOKEN/WHATSAPP_FROM)')
    client = Client(account_sid, auth_token)
    client = Client(account_sid, auth_token)
    # Twilio's WhatsApp API expects 'to' like 'whatsapp:+123456789'
    to = phone if phone.startswith('whatsapp:') else f'whatsapp:{phone}'
    message = client.messages.create(body=body, from_=from_whatsapp, to=to)
    logger.info('Sent WhatsApp message sid=%s to=%s', getattr(message, 'sid', None), to)
    return getattr(message, 'sid', None)
