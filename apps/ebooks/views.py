from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Ebook


class EbookListView(generics.ListAPIView):
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            Ebook.objects
            .filter(is_active=True)
            .select_related("author", "category")
            .order_by("-created_at")
        )

    def list(self, request):
        ebooks = self.get_queryset()
        data = []
        for e in ebooks:
            data.append({
                "id": e.id,
                "title": e.title,
                "author": e.author.name,
                "category": e.category.name if e.category else "Chưa phân loại",
                "category_slug": e.category.slug if e.category else None,
                "price": e.price,
                "cover": getattr(e, "cover_url", None),
            })
        return Response({"ebooks": data})


class EbookDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            Ebook.objects
            .filter(is_active=True)
            .select_related("author", "category")
        )

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
            "category": ebook.category.name if ebook.category else "Chưa phân loại",
            "category_slug": ebook.category.slug if ebook.category else None,
            "price": ebook.price,
            "cover": getattr(ebook, "cover_url", None),
            "file_url": getattr(ebook, "file_url", None),
            "file_mime": getattr(ebook, "file_mime", None),
        }
        return Response(data)