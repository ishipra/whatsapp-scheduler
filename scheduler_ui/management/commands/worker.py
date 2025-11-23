"""
Worker that pops message IDs from Redis queue and sends them via Twilio.
Updates DB status to 'sent' on success or 'failed' on error.
"""

import time
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import redis

from scheduler_ui.models import MessageQueue
from whatsapp_scheduler.actions import send_whatsapp_via_twilio

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Worker that processes messages from Redis queue and sends via Twilio"

    def add_arguments(self, parser):
        parser.add_argument(
            "--timeout",
            type=int,
            default=5,
            help="Redis BLPOP timeout in seconds (default: 5)",
        )

    def handle(self, *args, **options):
        timeout = options["timeout"]

        # Connect to Redis
        try:
            redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
            )
            # Test connection
            redis_client.ping()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}"
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to connect to Redis: {e}"))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'Worker started. Waiting for messages from queue "{settings.REDIS_QUEUE_KEY}". Press Ctrl+C to stop.'
            )
        )

        try:
            while True:
                # Blocking pop from Redis queue (waits up to timeout seconds)
                result = redis_client.blpop(settings.REDIS_QUEUE_KEY, timeout=timeout)

                if result is None:
                    # Timeout - no message available, continue loop
                    continue

                # result is a tuple: (queue_name, message_id)
                queue_name, message_id_str = result
                message_id = int(message_id_str)

                try:
                    # Get the message from database
                    msg = MessageQueue.objects.get(
                        id=message_id, status=MessageQueue.STATUS_ENQUEUED
                    )
                except MessageQueue.DoesNotExist:
                    logger.warning(
                        f"Message id={message_id} not found or not in enqueued status"
                    )
                    continue

                # Mark as processing
                with transaction.atomic():
                    msg.status = MessageQueue.STATUS_PROCESSING
                    msg.attempts += 1
                    msg.save()

                # Send the message
                try:
                    result_sid = send_whatsapp_via_twilio(
                        msg.phone, msg.body, msg.from_number
                    )
                    with transaction.atomic():
                        msg.status = MessageQueue.STATUS_SENT
                        msg.result = str(result_sid)
                        msg.processed_at = timezone.now()
                        msg.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Sent message id={msg.id} to {msg.phone} (sid: {result_sid})"
                        )
                    )
                except Exception as exc:
                    logger.exception(f"Failed sending message id={msg.id}")
                    with transaction.atomic():
                        msg.status = MessageQueue.STATUS_FAILED
                        msg.result = str(exc)
                        msg.processed_at = timezone.now()
                        msg.save()
                    self.stdout.write(
                        self.style.ERROR(f"Failed message id={msg.id}: {exc}")
                    )

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nWorker stopped."))
