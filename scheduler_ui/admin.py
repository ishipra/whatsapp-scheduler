from django.contrib import admin
from .models import MessageQueue


@admin.register(MessageQueue)
class MessageQueueAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "phone",
        "from_number",
        "status",
        "scheduled_time",
        "attempts",
        "created_at",
        "processed_at",
    )
    list_filter = ("status",)
    search_fields = ("phone", "body", "from_number")
    readonly_fields = ("created_at", "processed_at", "attempts", "result")
