from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_id', 'role', 'short_content', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__email', 'session_id', 'content']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def short_content(self, obj):
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content
    short_content.short_description = 'Nội dung'
