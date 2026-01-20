from django.urls import path
from . import views

urlpatterns = [
    path('deposit/', views.DepositView.as_view(), name='deposit'),
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
]
