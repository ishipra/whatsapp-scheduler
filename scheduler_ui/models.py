from django.db import models
from django.utils import timezone


class MessageQueue(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ENQUEUED = "enqueued"
    STATUS_PROCESSING = "processing"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ENQUEUED, "Enqueued"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
    ]

    phone = models.CharField(max_length=32)
    body = models.TextField()
    from_number = models.CharField(
        max_length=32, help_text="Twilio WhatsApp number (e.g., whatsapp:+1415...)"
    )
    scheduled_time = models.DateTimeField(help_text="When to send the message")
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    attempts = models.PositiveSmallIntegerField(default=0)
    result = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"MessageQueue(id={self.id}, phone={self.phone}, status={self.status})"
