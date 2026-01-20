import google.generativeai as genai
from django.conf import settings
from pgvector.django import CosineDistance
from apps.ebooks.models import Ebook


class RAGService:
    """Service for AI recommendations using Google Gemini with pgvector"""
    
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        # Google Gemini text-embedding-004 has 768 dimensions
        self.embedding_model = "models/text-embedding-004"
        self.chat_model = "models/gemini-3-flash-preview"
    
    def get_embedding(self, text):
        """Tạo embedding vector từ text sử dụng Gemini"""
        try:
            # Gemini embedding API
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
        # 1. Tạo embedding cho query
        try:
            # Task type retrieval_query is important for quality
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
        
        # 2. Tìm kiếm trong PostgreSQL vi pgvector
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
            context += f"""
{i}. **{ebook.title}**
   - Tác giả: {ebook.author.name}
   - Thể loại: {ebook.get_category_display()}
   - Giá: {ebook.price} Coins
   - Mô tả: {ebook.description[:200]}...
"""
        return context
    
    def chat(self, user_message):
        """Chat với AI sử dụng RAG (Gemini)"""
        # 1. Tìm sách liên quan
        relevant_ebooks = self.search_similar_ebooks(user_message, top_k=5)
        
        # 2. Xây dựng context
        context = self.build_context(relevant_ebooks)
        
        # 3. Gọi LLM với context
        system_prompt = f"""Bạn là trợ lý tư vấn sách cho cửa hàng ebook. Tên bạn là EbookAI.
        
Context data (Danh sách sách):
{context}

Yêu cầu:
- Dựa vào danh sách sách trên để trả lời câu hỏi của người dùng.
- Nếu tìm thấy sách phù hợp, hãy giới thiệu chi tiết và dẫn dắt người dùng mua.
- Nếu không có sách phù hợp trong danh sách, hãy xin lỗi và nói rõ.
- Trả lời bằng tiếng Việt, ngắn gọn, thân thiện, dùng emoji.
"""
        
        try:
            model = genai.GenerativeModel(self.chat_model)
            chat_session = model.start_chat(
                history=[
                    {"role": "user", "parts": [system_prompt]},
                    {"role": "model", "parts": ["Chào bạn! Tôi là EbookAI. Tôi đã sẵn sàng tư vấn sách cho bạn từ danh sách trên. Bạn cần tìm loại sách nào?"]}
                ]
            )
            
            response = chat_session.send_message(user_message)
            
            return {
                'response': response.text,
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
