from django.urls import path
from .views import (
    EbookListView,
    EbookDetailView,
    EbookReviewListView,
    EbookReviewCreateView,
)

urlpatterns = [
    path('', EbookListView.as_view(), name='ebook-list'),
    path('ebook/<int:pk>/', EbookDetailView.as_view(), name='ebook-detail-api'),

    path('ebook/<int:ebook_id>/reviews/', EbookReviewListView.as_view(), name='ebook-review-list'),
    path('ebook/<int:ebook_id>/reviews/create/', EbookReviewCreateView.as_view(), name='ebook-review-create'),
]