from django.db import models
from apps.accounts.models import User
from apps.ebooks.models import Ebook


class Transaction(models.Model):
    """Giao dịch nạp tiền và mua sách"""
    TYPE_CHOICES = [
        ('deposit', 'Nạp tiền'),
        ('purchase', 'Mua sách'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.IntegerField(help_text="+ khi nạp, - khi mua")
    ebook = models.ForeignKey(
        Ebook,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Chỉ có khi type='purchase'"
    )
    description = models.CharField(max_length=500)
    balance_after = models.PositiveIntegerField(help_text="Số dư sau giao dịch")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        verbose_name = 'Giao dịch'
        verbose_name_plural = 'Giao dịch'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.get_type_display()} - {self.amount} Coins"


class OwnedEbook(models.Model):
    """Sách user đã mua"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_ebooks')
    ebook = models.ForeignKey(Ebook, on_delete=models.CASCADE, related_name='owned_by')
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_ebook'
    )
    purchased_price = models.PositiveIntegerField()
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'owned_ebooks'
        verbose_name = 'Sách đã mua'
        verbose_name_plural = 'Sách đã mua'
        ordering = ['-purchased_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'ebook'], name='unique_user_owned_ebook')
        ]

    def __str__(self):
        return f"{self.user.email} - {self.ebook.title}"