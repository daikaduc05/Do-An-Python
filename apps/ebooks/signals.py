from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Ebook
from apps.ai_rag.services import RAGService

@receiver(post_save, sender=Ebook)
def create_embedding_on_save(sender, instance, created, **kwargs):
    if instance.is_active and instance.embedding is None:
        rag = RAGService()
        rag.create_ebook_embedding(instance)