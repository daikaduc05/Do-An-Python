from rest_framework.views import APIView
from rest_framework.response import Response
from .services import RAGService


class AIChatView(APIView):
    """Chat với AI sử dụng RAG"""
    
    def post(self, request):
        message = request.data.get('message', '')
        
        if not message:
            return Response({'error': 'Vui lòng nhập câu hỏi'}, status=400)
        
        rag_service = RAGService()
        result = rag_service.chat(message)
        
        return Response(result)


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
