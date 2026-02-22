"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

# یه تابع ساده برای صفحه اصلی
def home(request):
    return HttpResponse("""
        <h1>ربات فروشگاهی تلگرام</h1>
        <p>پروژه در حال توسعه است...</p>
        <p>برای ورود به ادمین: <a href="/admin/">/admin/</a></p>
    """)

urlpatterns = [
    path('', home),  # صفحه اصلی
    path('admin/', admin.site.urls),
    # path('shop/', include('shop.urls')),  # بعداً فعال می‌کنیم
    # path('wallet/', include('wallet.urls')),  # بعداً فعال می‌کنیم
    # path('bot/', include('bot.urls')),  # بعداً فعال می‌کنیم
]

# اضافه کردن مسیرهای مدیا برای حالت توسعه
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)