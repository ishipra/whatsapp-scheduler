
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json


from .models import MessageQueue


def index(request):
    """Render the basic UI with a button to trigger an action."""
    return render(request, 'scheduler_ui/index.html')


@require_POST
def trigger_action(request):
    """Accept JSON {phone, body} and create a MessageQueue entry.

    If no JSON provided, fallback to the simple placeholder action.
    """
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except Exception:
        payload = {}

    phone = payload.get('phone')
    body = payload.get('body')

    # If phone and body provided, enqueue the message
    if phone and body:
        mq = MessageQueue.objects.create(phone=phone, body=body)
        return JsonResponse({'success': True, 'queued_id': mq.id})

    # Otherwise, keep previous behavior: call placeholder action
    try:
        from whatsapp_scheduler.actions import trigger_action as do_trigger

        result = do_trigger()
    except Exception as exc:  # pragma: no cover - simple error path
        return JsonResponse({'success': False, 'error': str(exc)}, status=500)

    return JsonResponse({'success': True, 'result': result})


def status(request):
    return JsonResponse({'status': 'ok', 'time': timezone.now().isoformat()})
