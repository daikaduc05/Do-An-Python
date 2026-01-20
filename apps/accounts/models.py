from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with balance for virtual coins"""
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    balance = models.PositiveIntegerField(default=0, help_text="Số Coins hiện có")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
    
    def deposit(self, amount):
        """Nạp tiền vào tài khoản"""
        self.balance += amount
        self.save(update_fields=['balance'])
        return True
    
    def can_purchase(self, price):
        """Kiểm tra đủ tiền mua không"""
        return self.balance >= price
    
    def purchase(self, price):
        """Trừ tiền khi mua sách"""
        if self.can_purchase(price):
            self.balance -= price
            self.save(update_fields=['balance'])
            return True
        return False
