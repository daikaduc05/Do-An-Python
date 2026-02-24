"""
LangChain Memory Integration for Django Chat
Sử dụng user_id làm session_id để lưu trữ lịch sử hội thoại
"""

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing import List


class DjangoChatMessageHistory(BaseChatMessageHistory):
    """
    Custom LangChain ChatMessageHistory sử dụng Django ORM.
    Lưu trữ tin nhắn vào PostgreSQL thông qua model ChatMessage.
    Sử dụng user_id làm session_id.
    """
    
    def __init__(self, session_id: str, user=None):
        """
        Args:
            session_id: ID phiên chat (= user_id)
            user: Django User object
        """
        self.session_id = str(session_id)
        self.user = user
    
    @property
    def messages(self) -> List[BaseMessage]:
        """Lấy tất cả tin nhắn từ database theo session_id"""
        from .models import ChatMessage
        
        db_messages = ChatMessage.objects.filter(
            session_id=self.session_id
        ).order_by('created_at')
        
        messages = []
        for msg in db_messages:
            if msg.role == 'human':
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == 'ai':
                messages.append(AIMessage(content=msg.content))
        
        return messages
    
    def add_message(self, message: BaseMessage) -> None:
        """Thêm tin nhắn mới vào database"""
        from .models import ChatMessage
        
        if isinstance(message, HumanMessage):
            role = 'human'
        elif isinstance(message, AIMessage):
            role = 'ai'
        else:
            role = 'human'  # Default
        
        ChatMessage.objects.create(
            user=self.user,
            session_id=self.session_id,
            role=role,
            content=message.content,
        )
    
    def add_user_message(self, message: str) -> None:
        """Thêm tin nhắn của người dùng"""
        self.add_message(HumanMessage(content=message))
    
    def add_ai_message(self, message: str) -> None:
        """Thêm tin nhắn của AI"""
        self.add_message(AIMessage(content=message))
    
    def clear(self) -> None:
        """Xóa toàn bộ lịch sử chat của session"""
        from .models import ChatMessage
        
        ChatMessage.objects.filter(session_id=self.session_id).delete()
    
    def get_recent_messages(self, limit: int = 20) -> List[BaseMessage]:
        """Lấy N tin nhắn gần nhất (tối ưu hiệu suất)"""
        from .models import ChatMessage
        
        db_messages = ChatMessage.objects.filter(
            session_id=self.session_id
        ).order_by('-created_at')[:limit]
        
        # Reverse lại đúng thứ tự thời gian
        db_messages = list(reversed(db_messages))
        
        messages = []
        for msg in db_messages:
            if msg.role == 'human':
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == 'ai':
                messages.append(AIMessage(content=msg.content))
        
        return messages
