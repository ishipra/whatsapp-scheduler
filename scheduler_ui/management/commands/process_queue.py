from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
import os
import logging

from scheduler_ui.models import MessageQueue
from whatsapp_scheduler.actions import send_whatsapp_via_twilio

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Process pending MessageQueue entries and send them via WhatsApp (Twilio)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit", type=int, default=10, help="Maximum messages to process"
        )

    def handle(self, *args, **options):
        limit = options["limit"]
        processed = 0

        qs = MessageQueue.objects.filter(status=MessageQueue.STATUS_PENDING).order_by(
            "created_at"
        )[:limit]

        for msg in qs:
            with transaction.atomic():
                # mark processing
                msg.status = MessageQueue.STATUS_PROCESSING
                msg.attempts += 1
                msg.save()

            try:
                # Check if from_number exists (for backward compatibility)
                if not hasattr(msg, "from_number") or not msg.from_number:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Message id={msg.id} missing from_number, skipping"
                        )
                    )
                    msg.status = MessageQueue.STATUS_FAILED
                    msg.result = "Missing from_number field"
                    msg.processed_at = timezone.now()
                    msg.save()
                    processed += 1
                    continue

                result = send_whatsapp_via_twilio(msg.phone, msg.body, msg.from_number)
                msg.status = MessageQueue.STATUS_SENT
                msg.result = str(result)
                msg.processed_at = timezone.now()
                msg.save()
                self.stdout.write(
                    self.style.SUCCESS(f"Sent id={msg.id} to {msg.phone}")
                )
            except Exception as exc:
                logger.exception("Failed sending message id=%s", msg.id)
                msg.status = MessageQueue.STATUS_FAILED
                msg.result = str(exc)
                msg.processed_at = timezone.now()
                msg.save()
                self.stdout.write(self.style.ERROR(f"Failed id={msg.id}: {exc}"))

            processed += 1

        self.stdout.write(self.style.SUCCESS(f"Processed {processed} messages"))
