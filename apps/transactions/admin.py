from django.contrib import admin
from .models import Transaction, OwnedEbook


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'amount', 'ebook', 'balance_after', 'created_at']
    list_filter = ['type', 'created_at']
    search_fields = ['user__email', 'description', 'ebook__title']
    autocomplete_fields = ['user', 'ebook']
    readonly_fields = ['created_at']


@admin.register(OwnedEbook)
class OwnedEbookAdmin(admin.ModelAdmin):
    list_display = ['user', 'ebook', 'purchased_price', 'purchased_at']
    search_fields = ['user__email', 'ebook__title']
    autocomplete_fields = ['user', 'ebook', 'transaction']
    readonly_fields = ['purchased_at']