from django.contrib import admin
from .models import MessageQueue


@admin.register(MessageQueue)
class MessageQueueAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'status', 'attempts', 'created_at', 'processed_at')
    list_filter = ('status',)
    search_fields = ('phone', 'body')
