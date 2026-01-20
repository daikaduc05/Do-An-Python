from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Ebook


@receiver(post_save, sender=Ebook)
def create_embedding_on_save(sender, instance, created, **kwargs):
    """Tự động tạo embedding khi thêm/sửa ebook"""
    if instance.is_active and not instance.embedding:
        from apps.ai_rag.services import RAGService
        rag_service = RAGService()
        rag_service.create_ebook_embedding(instance)
