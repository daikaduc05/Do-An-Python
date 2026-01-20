from django.db import models
from pgvector.django import VectorField


class Author(models.Model):
    """Tác giả sách"""
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='authors/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'authors'
        verbose_name = 'Tác giả'
        verbose_name_plural = 'Tác giả'
    
    def __str__(self):
        return self.name


class Ebook(models.Model):
    """Sách điện tử"""
    CATEGORY_CHOICES = [
        ('fiction', 'Tiểu thuyết'),
        ('science', 'Khoa học'),
        ('business', 'Kinh doanh'),
        ('self_help', 'Phát triển bản thân'),
        ('technology', 'Công nghệ'),
        ('history', 'Lịch sử'),
        ('children', 'Thiếu nhi'),
        ('other', 'Khác'),
    ]
    
    title = models.CharField(max_length=500)
    description = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='ebooks')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.PositiveIntegerField(help_text="Giá bằng Coins")
    # file_url = models.FileField(upload_to='ebooks/', null=True, blank=True)
    file_url = models.FileField(upload_to='ebooks/')
    cover_image = models.ImageField(upload_to='covers/')
    
    # Vector embedding cho RAG (Google Gemini text-embedding-004: 768 dimensions)
    embedding = VectorField(dimensions=768, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ebooks'
        verbose_name = 'Ebook'
        verbose_name_plural = 'Ebooks'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_text_for_embedding(self):
        """Text để tạo embedding"""
        return f"{self.title}. {self.author.name}. {self.get_category_display()}. {self.description}"
