from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Ebook
from rest_framework.response import Response


class EbookListView(generics.ListAPIView):
    """List all ebooks"""
    queryset = Ebook.objects.filter(is_active=True)
    permission_classes = [AllowAny]
    
    def list(self, request):
        ebooks = self.get_queryset()
        data = [{
            'id': e.id,
            'title': e.title,
            'author': e.author.name,
            'category': e.get_category_display(),
            'price': e.price,
            'cover': e.cover_image.url if e.cover_image else None,
        } for e in ebooks]
        return Response({'ebooks': data})


class EbookDetailView(generics.RetrieveAPIView):
    """Get ebook detail"""
    queryset = Ebook.objects.filter(is_active=True)
    permission_classes = [AllowAny]
    
    def retrieve(self, request, *args, **kwargs):
        ebook = self.get_object()
        data = {
            'id': ebook.id,
            'title': ebook.title,
            'description': ebook.description,
            'author': {
                'id': ebook.author.id,
                'name': ebook.author.name,
                'bio': ebook.author.bio,
            },
            'category': ebook.get_category_display(),
            'price': ebook.price,
            'cover': ebook.cover_image.url if ebook.cover_image else None,
        }
        return Response(data)
