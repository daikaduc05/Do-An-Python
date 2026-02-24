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


class Category(models.Model):
    """Thể loại sách"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Thể loại'
        verbose_name_plural = 'Thể loại'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Ebook(models.Model):
    """Sách điện tử"""
    
    title = models.CharField(max_length=500)
    description = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='ebooks')
    category = models.CharField(max_length=100, blank=True, default='')
    price = models.PositiveIntegerField(help_text="Giá bằng Coins")
    # file_url = models.FileField(upload_to='ebooks/', null=True, blank=True)
    file_url = models.FileField(upload_to='ebooks/')
    cover_image = models.ImageField(upload_to='covers/')
    
    # Vector embedding cho RAG (Google Gemini gemini-embedding-001: 3072 dimensions)
    embedding = VectorField(dimensions=3072, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ebooks'
        verbose_name = 'Ebook'
        verbose_name_plural = 'Ebooks'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_category_display(self):
        """Trả về tên thể loại"""
        return self.category if self.category else 'Chưa phân loại'
    
    def get_text_for_embedding(self):
        """Text để tạo embedding"""
        return f"{self.title}. {self.author.name}. {self.get_category_display()}. {self.description}"
