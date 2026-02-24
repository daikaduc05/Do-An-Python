from django.db import models
from django.conf import settings


class ChatMessage(models.Model):
    """Lưu trữ lịch sử chat của người dùng với AI"""
    
    ROLE_CHOICES = [
        ('human', 'Human'),
        ('ai', 'AI'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        help_text="Người dùng sở hữu tin nhắn"
    )
    session_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Session ID = user_id để nhóm các tin nhắn"
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        help_text="Vai trò: human hoặc ai"
    )
    content = models.TextField(
        help_text="Nội dung tin nhắn"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Thời gian tạo tin nhắn"
    )
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        indexes = [
            models.Index(fields=['session_id', 'created_at']),
        ]
    
    def __str__(self):
        return f"[{self.role}] {self.content[:50]}..."
