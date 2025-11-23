"""
Scheduler loop that runs every 30 seconds.
Finds messages where scheduled_time <= now AND status = 'pending',
pushes their IDs to Redis queue, and updates status to 'enqueued'.
"""

import time
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import redis

from scheduler_ui.models import MessageQueue

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Scheduler loop that runs every 30 seconds to enqueue ready messages"

    def add_arguments(self, parser):
        parser.add_argument(
            "--interval",
            type=int,
            default=30,
            help="Interval in seconds between scheduler runs (default: 30)",
        )

    def handle(self, *args, **options):
        interval = options["interval"]

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
                f"Starting scheduler loop (interval: {interval}s). Press Ctrl+C to stop."
            )
        )

        try:
            while True:
                now = timezone.now()

                # Find messages ready to be sent
                ready_messages = MessageQueue.objects.filter(
                    status=MessageQueue.STATUS_PENDING, scheduled_time__lte=now
                ).order_by("scheduled_time")

                enqueued_count = 0
                for msg in ready_messages:
                    try:
                        with transaction.atomic():
                            # Update status to enqueued
                            msg.status = MessageQueue.STATUS_ENQUEUED
                            msg.save()

                            # Push to Redis queue
                            redis_client.lpush(settings.REDIS_QUEUE_KEY, str(msg.id))
                            enqueued_count += 1
                            self.stdout.write(
                                f"Enqueued message id={msg.id} (scheduled for {msg.scheduled_time})"
                            )
                    except Exception as e:
                        logger.exception(f"Failed to enqueue message id={msg.id}: {e}")
                        # Revert status on error
                        msg.status = MessageQueue.STATUS_PENDING
                        msg.save()

                if enqueued_count > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f"Enqueued {enqueued_count} message(s)")
                    )

                # Sleep for the interval
                time.sleep(interval)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nScheduler loop stopped."))
