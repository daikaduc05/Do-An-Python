from django.shortcuts import render
from django.views import View


class HomeView(View):
    """Homepage with ebook listing"""
    def get(self, request):
        return render(request, 'home.html')


class AIChatView(View):
    """AI Chat interface"""
    def get(self, request):
        return render(request, 'ai_chat.html')


class EbookDetailView(View):
    """Ebook detail page"""
    def get(self, request, ebook_id):
        return render(request, 'ebook_detail.html', {'ebook_id': ebook_id})
