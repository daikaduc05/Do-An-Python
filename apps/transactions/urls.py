from django.urls import path
from . import views

urlpatterns = [
    path('deposit/', views.DepositView.as_view(), name='deposit'),
    path('purchase/', views.PurchaseEbookView.as_view(), name='purchase-ebook'),
    path('library/', views.MyLibraryView.as_view(), name='my-library'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
]