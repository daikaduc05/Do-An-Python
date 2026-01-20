from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # API Endpoints (Prefix /api/)
    path("api/ebooks/", include("apps.ebooks.urls")),
    path("api/transactions/", include("apps.transactions.urls")),
    path("api/ai/", include("apps.ai_rag.urls")),
    
    # Auth Views (Login/Register)
    path("", include("apps.accounts.urls")),
    
    # Frontend Pages (Template Views)
    path("", views.HomeView.as_view(), name='home'),
    path("ai-chat/", views.AIChatView.as_view(), name='ai-chat'),
    path("ebook/<int:ebook_id>/", views.EbookDetailView.as_view(), name='ebook-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
