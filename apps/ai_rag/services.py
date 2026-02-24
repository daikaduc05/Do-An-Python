"""
RAG Service tích hợp LangChain Memory
Sử dụng ChatGoogleGenerativeAI + DjangoChatMessageHistory
"""

import google.generativeai as genai
from django.conf import settings
from pgvector.django import CosineDistance
from apps.ebooks.models import Ebook

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from .memory import DjangoChatMessageHistory


class RAGService:
    """Service for AI recommendations using Google Gemini with pgvector + LangChain Memory"""
    
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        # Google Gemini gemini-embedding-001 has 3072 dimensions
        self.embedding_model = "models/gemini-embedding-001"
        
        # LangChain ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.7,
        )
    
    def get_embedding(self, text):
        """Tạo embedding vector từ text sử dụng Gemini"""
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document",
                title="Embedding of ebook text"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error creating embedding: {e}")
            return None
    
    def search_similar_ebooks(self, query, top_k=5):
        """Tìm ebook tương tự bằng vector similarity"""
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=query,
                task_type="retrieval_query"
            )
            query_embedding = result['embedding']
        except Exception as e:
            print(f"Error creating query embedding: {e}")
            return Ebook.objects.none()
            
        if not query_embedding:
            return Ebook.objects.none()
        
        similar_ebooks = Ebook.objects.filter(
            is_active=True,
            embedding__isnull=False
        ).annotate(
            distance=CosineDistance('embedding', query_embedding)
        ).order_by('distance')[:top_k]
        
        return similar_ebooks
    
    def build_context(self, ebooks):
        """Xây dựng context từ danh sách ebook"""
        context = "Danh sách sách có trong cửa hàng:\n\n"
        
        for i, ebook in enumerate(ebooks, 1):
            try:
                category_name = ebook.get_category_display()
            except Exception:
                category_name = 'Chưa phân loại'
            
            context += f"""
{i}. **{ebook.title}**
   - Tác giả: {ebook.author.name}
   - Thể loại: {category_name}
   - Giá: {ebook.price} Coins
   - Mô tả: {ebook.description[:200]}...
"""
        return context
    
    def chat(self, user_message, user=None):
        """
        Chat với AI sử dụng RAG + LangChain Memory.
        
        Args:
            user_message: Tin nhắn từ người dùng
            user: Django User object (để lấy user_id làm session_id)
        
        Returns:
            dict với response và relevant_ebooks
        """
        # 1. Tìm sách liên quan bằng RAG
        relevant_ebooks = self.search_similar_ebooks(user_message, top_k=5)
        
        # 2. Xây dựng context từ kết quả RAG
        context = self.build_context(relevant_ebooks)
        
        # 3. Lấy session_id từ user_id
        session_id = str(user.id) if user and user.is_authenticated else "anonymous"
        
        # 4. Tạo memory history cho user
        chat_history = DjangoChatMessageHistory(
            session_id=session_id,
            user=user if user and user.is_authenticated else None
        )
        
        # 5. Xây dựng messages cho LangChain
        system_prompt = f"""Bạn là trợ lý tư vấn sách cho cửa hàng ebook. Tên bạn là EbookAI.
        
Context data (Danh sách sách liên quan đến câu hỏi hiện tại):
{context}

Yêu cầu:
- Dựa vào danh sách sách trên để trả lời câu hỏi của người dùng.
- Nếu tìm thấy sách phù hợp, hãy giới thiệu chi tiết và dẫn dắt người dùng mua.
- Nếu không có sách phù hợp trong danh sách, hãy xin lỗi và nói rõ.
- Trả lời bằng tiếng Việt, ngắn gọn, thân thiện, dùng emoji.
- Bạn có thể nhớ các cuộc hội thoại trước đó với người dùng.
- Nếu người dùng hỏi về sách đã tư vấn trước đó, hãy tham khảo lịch sử chat.
"""
        
        try:
            # Lấy lịch sử chat gần nhất (giới hạn 20 tin nhắn để tối ưu)
            history_messages = chat_history.get_recent_messages(limit=20)
            
            # Xây dựng danh sách messages cho LLM
            messages = [SystemMessage(content=system_prompt)]
            messages.extend(history_messages)
            messages.append(HumanMessage(content=user_message))
            
            # Gọi LLM
            response = self.llm.invoke(messages)
            ai_response = response.content
            
            # Lưu tin nhắn vào memory (chỉ lưu cho authenticated users)
            if user and user.is_authenticated:
                chat_history.add_user_message(user_message)
                chat_history.add_ai_message(ai_response)
            
            return {
                'response': ai_response,
                'relevant_ebooks': [
                    {
                        'id': e.id,
                        'title': e.title,
                        'author': e.author.name,
                        'price': e.price,
                        'cover': e.cover_image.url if e.cover_image else None
                    }
                    for e in relevant_ebooks
                ]
            }
        except Exception as e:
            return {
                'response': f'Xin lỗi, hệ thống AI đang bận hoặc gặp lỗi kết nối: {str(e)}',
                'relevant_ebooks': []
            }
    
    def get_chat_history(self, user):
        """
        Lấy lịch sử chat của user để hiển thị trên frontend.
        
        Args:
            user: Django User object
        
        Returns:
            list of dict với role và content
        """
        from .models import ChatMessage
        
        if not user or not user.is_authenticated:
            return []
        
        session_id = str(user.id)
        messages = ChatMessage.objects.filter(
            session_id=session_id
        ).order_by('created_at').values('role', 'content', 'created_at')
        
        return [
            {
                'role': msg['role'],
                'content': msg['content'],
                'created_at': msg['created_at'].isoformat()
            }
            for msg in messages
        ]
    
    def clear_chat_history(self, user):
        """
        Xóa toàn bộ lịch sử chat của user.
        
        Args:
            user: Django User object
        
        Returns:
            bool
        """
        if not user or not user.is_authenticated:
            return False
        
        session_id = str(user.id)
        chat_history = DjangoChatMessageHistory(
            session_id=session_id,
            user=user
        )
        chat_history.clear()
        return True
    
    def create_ebook_embedding(self, ebook):
        """Tạo embedding cho 1 ebook (gọi khi thêm/sửa sách)"""
        text = ebook.get_text_for_embedding()
        embedding = self.get_embedding(text)
        
        if embedding:
            ebook.embedding = embedding
            ebook.save(update_fields=['embedding'])
            return True
        return False
    
    def update_all_embeddings(self):
        """Cập nhật embedding cho tất cả ebook"""
        ebooks = Ebook.objects.filter(is_active=True)
        
        success_count = 0
        for ebook in ebooks:
            if self.create_ebook_embedding(ebook):
                success_count += 1
                print(f"Created Gemini embedding for: {ebook.title}")
        
        return success_count
