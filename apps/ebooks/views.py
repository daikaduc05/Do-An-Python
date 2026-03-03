from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Ebook


class EbookListView(generics.ListAPIView):
    queryset = Ebook.objects.filter(is_active=True)
    permission_classes = [AllowAny]

    def list(self, request):
        ebooks = self.get_queryset()
        data = [{
            "id": e.id,
            "title": e.title,
            "author": e.author.name,
            "category": e.get_category_display(),
            "price": e.price,
            "cover": getattr(e, "cover_url", None),  
        } for e in ebooks]
        return Response({"ebooks": data})


class EbookDetailView(generics.RetrieveAPIView):
    queryset = Ebook.objects.filter(is_active=True)
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        ebook = self.get_object()
        data = {
            "id": ebook.id,
            "title": ebook.title,
            "description": ebook.description,
            "author": {
                "id": ebook.author.id,
                "name": ebook.author.name,
                "bio": ebook.author.bio,
            },
            "category": ebook.get_category_display(),
            "price": ebook.price,
            "cover": getattr(ebook, "cover_url", None), 

            "file_url": getattr(ebook, "file_url", None),
            "file_mime": getattr(ebook, "file_mime", None),
        }
        return Response(data)