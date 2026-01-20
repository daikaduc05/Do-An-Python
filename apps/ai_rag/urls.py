from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.AIChatView.as_view(), name='ai-chat'),
    path('search/', views.SemanticSearchView.as_view(), name='semantic-search'),
]
