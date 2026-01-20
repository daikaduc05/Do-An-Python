from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'balance', 'created_at']
    search_fields = ['email', 'username']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']
