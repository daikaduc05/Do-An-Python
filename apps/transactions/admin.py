from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'amount', 'balance_after', 'created_at']
    search_fields = ['user__email']
    list_filter = ['type', 'created_at']
    readonly_fields = ['created_at']
