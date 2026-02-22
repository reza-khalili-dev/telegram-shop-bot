from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class TelegramUser(models.Model):
    """
    مدل کاربران تلگرام
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram', null=True, blank=True)
    telegram_id = models.BigIntegerField('آیدی تلگرام', unique=True)
    username = models.CharField('یوزرنیم', max_length=255, blank=True, null=True)
    first_name = models.CharField('نام', max_length=255, blank=True, null=True)
    last_name = models.CharField('نام خانوادگی', max_length=255, blank=True, null=True)
    phone_number = models.CharField('شماره موبایل', max_length=15, blank=True, null=True)
    language_code = models.CharField('کد زبان', max_length=10, default='fa')
    is_active = models.BooleanField('فعال', default=True)
    created_at = models.DateTimeField('تاریخ عضویت', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'کاربر تلگرام'
        verbose_name_plural = 'کاربران تلگرام'

    def __str__(self):
        return f"{self.first_name or self.telegram_id}"

class UserState(models.Model):
    """
    مدل وضعیت کاربر در مکالمه‌های ربات
    """
    user = models.OneToOneField(TelegramUser, on_delete=models.CASCADE, related_name='state')
    current_state = models.CharField('وضعیت فعلی', max_length=50, default='main_menu')
    temp_data = models.JSONField('داده‌های موقت', default=dict, blank=True)
    updated_at = models.DateTimeField('آخرین بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'وضعیت کاربر'
        verbose_name_plural = 'وضعیت کاربران'

    def __str__(self):
        return f"{self.user} - {self.current_state}"

# سیگنال برای ساخت خودکار Wallet موقع ساخت User
@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        from wallet.models import Wallet
        Wallet.objects.create(user=instance)