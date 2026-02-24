from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.AIChatView.as_view(), name='ai-chat'),
    path('chat/history/', views.ChatHistoryView.as_view(), name='chat-history'),
    path('search/', views.SemanticSearchView.as_view(), name='semantic-search'),
]
