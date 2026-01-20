from django.contrib import admin
from .models import Author, Ebook


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Ebook)
class EbookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'price', 'is_active', 'created_at']
    search_fields = ['title', 'author__name']
    list_filter = ['category', 'is_active', 'created_at']
    readonly_fields = ['embedding', 'created_at']
