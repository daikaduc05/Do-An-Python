from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .services import RAGService


class AIChatView(APIView):
    """Chat với AI sử dụng RAG + LangChain Memory"""
    
    def post(self, request):
        message = request.data.get('message', '')
        
        if not message:
            return Response({'error': 'Vui lòng nhập câu hỏi'}, status=400)
        
        rag_service = RAGService()
        # Truyền user để sử dụng user_id làm session_id cho memory
        result = rag_service.chat(message, user=request.user)
        
        return Response(result)


class ChatHistoryView(APIView):
    """Lấy lịch sử chat của user hiện tại"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Lấy toàn bộ lịch sử chat"""
        rag_service = RAGService()
        history = rag_service.get_chat_history(request.user)
        
        return Response({
            'history': history,
            'session_id': str(request.user.id)
        })
    
    def delete(self, request):
        """Xóa toàn bộ lịch sử chat (New Chat)"""
        rag_service = RAGService()
        success = rag_service.clear_chat_history(request.user)
        
        if success:
            return Response({'message': 'Đã xóa lịch sử chat'})
        return Response({'error': 'Không thể xóa lịch sử'}, status=400)


class SemanticSearchView(APIView):
    """Tìm kiếm semantic bằng vector"""
    
    def get(self, request):
        query = request.query_params.get('q', '')
        
        if not query:
            return Response({'error': 'Vui lòng nhập từ khóa'}, status=400)
        
        rag_service = RAGService()
        ebooks = rag_service.search_similar_ebooks(query, top_k=10)
        
        data = [{
            'id': e.id,
            'title': e.title,
            'author': e.author.name,
            'category': e.get_category_display(),
            'price': e.price,
            'cover': e.cover_image.url if e.cover_image else None,
        } for e in ebooks]
        
        return Response({'results': data})
