from django.urls import path
from . import views

urlpatterns = [
    path('', views.EbookListView.as_view(), name='home'),
    path('ebook/<int:pk>/', views.EbookDetailView.as_view(), name='ebook-detail'),
]
