from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from .models import Ebook, EbookReview, EbookReviewImage
from apps.transactions.models import OwnedEbook
from django.db.models import Avg, Count

class EbookPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50


class EbookListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    pagination_class = EbookPagination

    def get_queryset(self):
        return (
            Ebook.objects
            .filter(is_active=True)
            .select_related("author", "category")
            .order_by("-created_at")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        data = []
        for e in page:
            data.append({
                "id": e.id,
                "title": e.title,
                "author": e.author.name if e.author else "Chưa có tác giả",
                "category": e.category.name if e.category else "Chưa phân loại",
                "category_slug": e.category.slug if e.category else None,
                "price": e.price,
                "cover": getattr(e, "cover_url", None),
            })

        return self.get_paginated_response(data)
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

        is_owned = False
        if request.user.is_authenticated:
            is_owned = OwnedEbook.objects.filter(user=request.user, ebook=ebook).exists()

        rating_data = ebook.reviews.aggregate(
            rating_avg=Avg('rating'),
            rating_count=Count('id'),
        )

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
            "file_mime": getattr(ebook, "file_mime", None),
            "is_owned": is_owned,
            "can_review": is_owned,
            "rating_avg": round(rating_data["rating_avg"] or 0, 1),
            "rating_count": rating_data["rating_count"] or 0,
            "preview_url": getattr(ebook, "file_url", None),
            "file_url": getattr(ebook, "file_url", None) if is_owned else None,
        }
        return Response(data)
    
class EbookReviewListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, ebook_id):
        try:
            ebook = Ebook.objects.get(id=ebook_id, is_active=True)
        except Ebook.DoesNotExist:
            return Response({'error': 'Sách không tồn tại'}, status=404)

        reviews = (
            EbookReview.objects
            .filter(ebook=ebook)
            .select_related('user')
            .prefetch_related('images')
            .order_by('-created_at')
        )

        rating_data = reviews.aggregate(
            rating_avg=Avg('rating'),
            rating_count=Count('id'),
        )

        data = []
        for review in reviews:
            data.append({
                'id': review.id,
                'user': {
                    'email': review.user.email,
                    'display_name': review.user.email.split('@')[0],
                },
                'rating': review.rating,
                'content': review.content,
                'created_at': review.created_at.isoformat(),
                'images': [
                    {
                        'id': image.id,
                        'url': image.image.url,
                    }
                    for image in review.images.all()
                ]
            })

        return Response({
            'rating_avg': round(rating_data['rating_avg'] or 0, 1),
            'rating_count': rating_data['rating_count'] or 0,
            'reviews': data,
        })
    
class EbookReviewCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, ebook_id):
        try:
            ebook = Ebook.objects.get(id=ebook_id, is_active=True)
        except Ebook.DoesNotExist:
            return Response({'error': 'Sách không tồn tại'}, status=404)

        has_owned = OwnedEbook.objects.filter(user=request.user, ebook=ebook).exists()
        if not has_owned:
            return Response(
                {'error': 'Chỉ người đã mua sách mới được đánh giá'},
                status=status.HTTP_403_FORBIDDEN
            )

        rating = request.data.get('rating')
        content = (request.data.get('content') or '').strip()

        try:
            rating = int(rating)
        except (TypeError, ValueError):
            return Response({'error': 'Số sao không hợp lệ'}, status=400)

        if rating < 1 or rating > 5:
            return Response({'error': 'Số sao phải từ 1 đến 5'}, status=400)

        review, created = EbookReview.objects.update_or_create(
            ebook=ebook,
            user=request.user,
            defaults={
                'rating': rating,
                'content': content,
            }
        )

        uploaded_images = request.FILES.getlist('images')
        if uploaded_images:
            review.images.all().delete()
            for image in uploaded_images[:4]:
                EbookReviewImage.objects.create(review=review, image=image)

        return Response({
            'message': 'Đánh giá thành công' if created else 'Cập nhật đánh giá thành công',
            'review_id': review.id,
        }, status=201 if created else 200)