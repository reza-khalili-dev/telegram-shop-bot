from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

class Product(models.Model):
    """
    مدل محصول - فقط یک محصول داریم (تک محصول)
    """
    name = models.CharField('نام محصول', max_length=200)
    description = models.TextField('توضیحات محصول')
    price = models.DecimalField('قیمت (تومان)', max_digits=10, decimal_places=0, 
                                validators=[MinValueValidator(1000)])
    image = models.ImageField('تصویر محصول', upload_to='products/')
    is_active = models.BooleanField('فعال است؟', default=True)
    stock = models.PositiveIntegerField('موجودی', default=0)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('تاریخ بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'

    def __str__(self):
        return self.name

    def is_available(self):
        """بررسی موجودی محصول"""
        return self.is_active and self.stock > 0


class Order(models.Model):
    """
    مدل سفارش
    """
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('processing', 'در حال پردازش'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل شده'),
        ('cancelled', 'لغو شده'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders',
                            verbose_name='کاربر')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orders',
                               verbose_name='محصول')
    quantity = models.PositiveIntegerField('تعداد', default=1)
    total_price = models.DecimalField('قیمت کل', max_digits=10, decimal_places=0)
    status = models.CharField('وضعیت', max_length=10, choices=STATUS_CHOICES, default='pending')
    transaction = models.OneToOneField('wallet.Transaction', on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='order',
                                      verbose_name='تراکنش')
    created_at = models.DateTimeField('تاریخ سفارش', auto_now_add=True)
    updated_at = models.DateTimeField('تاریخ بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f"سفارش {self.id} - {self.user.username} - {self.product.name}"