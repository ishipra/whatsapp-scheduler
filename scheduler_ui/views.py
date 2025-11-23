from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
import json
import os


from .models import MessageQueue


def index(request):
    """Render the basic UI with a button to trigger an action."""
    return render(request, "scheduler_ui/index.html")


@csrf_exempt
@require_POST
def trigger_action(request):
    """Accept JSON {phone, body, scheduled_time} and create a MessageQueue entry.

    Required fields:
    - phone: Recipient phone number
    - body: Message body
    - scheduled_time: ISO format datetime string (e.g., '2024-01-01T12:00:00Z')

    The Twilio WhatsApp number (from_number) is taken from TWILIO_WHATSAPP_FROM env variable.
    If required fields are missing, returns error.
    """
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except Exception as e:
        return JsonResponse(
            {"success": False, "error": f"Invalid JSON: {str(e)}"}, status=400
        )

    phone = payload.get("phone")
    body = payload.get("body")
    scheduled_time_str = payload.get("scheduled_time")

    # Get from_number from environment variable (fallback to settings)
    from_number = os.environ.get("TWILIO_WHATSAPP_FROM") or getattr(
        settings, "TWILIO_WHATSAPP_FROM", ""
    )

    # Validate required fields
    if not phone:
        return JsonResponse(
            {"success": False, "error": "phone is required"}, status=400
        )
    if not body:
        return JsonResponse({"success": False, "error": "body is required"}, status=400)
    if not from_number:
        return JsonResponse(
            {
                "success": False,
                "error": "TWILIO_WHATSAPP_FROM environment variable is not set",
            },
            status=400,
        )
    if not scheduled_time_str:
        return JsonResponse(
            {"success": False, "error": "scheduled_time is required"}, status=400
        )

    # Parse scheduled_time
    try:
        from dateutil import parser as date_parser

        scheduled_time = date_parser.parse(scheduled_time_str)
        # Ensure timezone-aware
        if scheduled_time.tzinfo is None:
            scheduled_time = timezone.make_aware(scheduled_time)
    except Exception as e:
        return JsonResponse(
            {"success": False, "error": f"Invalid scheduled_time format: {str(e)}"},
            status=400,
        )

    # Validate scheduled_time is in the future
    if scheduled_time <= timezone.now():
        return JsonResponse(
            {"success": False, "error": "scheduled_time must be in the future"},
            status=400,
        )

    # Create the message queue entry
    try:
        mq = MessageQueue.objects.create(
            phone=phone,
            body=body,
            from_number=from_number,
            scheduled_time=scheduled_time,
            status=MessageQueue.STATUS_PENDING,
        )
        return JsonResponse(
            {
                "success": True,
                "queued_id": mq.id,
                "scheduled_time": scheduled_time.isoformat(),
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def status(request):
    return JsonResponse({"status": "ok", "time": timezone.now().isoformat()})
