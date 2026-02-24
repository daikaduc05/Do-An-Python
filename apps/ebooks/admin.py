from django.contrib import admin
from .models import Author, Category, Ebook


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ebook)
class EbookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'price', 'is_active', 'created_at']
    search_fields = ['title', 'author__name']
    list_filter = ['category', 'is_active', 'created_at']
    readonly_fields = ['embedding', 'created_at']

