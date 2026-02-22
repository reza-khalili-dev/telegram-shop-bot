from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Wallet(models.Model):
    """
    مدل کیف پول کاربر
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet', 
                                verbose_name='کاربر')
    balance = models.DecimalField('موجودی (تومان)', max_digits=10, decimal_places=0, 
                                  default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('تاریخ بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'کیف پول'
        verbose_name_plural = 'کیف پول‌ها'

    def __str__(self):
        return f"{self.user.username} - {self.balance:,} تومان"

    def deposit(self, amount):
        """افزایش موجودی"""
        self.balance += amount
        self.save()
        return self.balance

    def withdraw(self, amount):
        """کاهش موجودی (بررسی موجودی کافی قبل از فراخوانی)"""
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False


class Transaction(models.Model):
    """
    مدل تراکنش‌های مالی
    """
    TRANSACTION_TYPES = [
        ('deposit', 'واریز'),
        ('withdraw', 'برداشت'),
        ('purchase', 'خرید'),
    ]

    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
        ('cancelled', 'لغو شده'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions',
                              verbose_name='کیف پول')
    amount = models.DecimalField('مبلغ (تومان)', max_digits=10, decimal_places=0)
    transaction_type = models.CharField('نوع تراکنش', max_length=10, choices=TRANSACTION_TYPES)
    status = models.CharField('وضعیت', max_length=10, choices=STATUS_CHOICES, default='pending')
    description = models.TextField('توضیحات', blank=True)
    created_at = models.DateTimeField('تاریخ', auto_now_add=True)

    class Meta:
        verbose_name = 'تراکنش'
        verbose_name_plural = 'تراکنش‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount:,} تومان - {self.get_status_display()}"