from django.contrib import admin
from django.urls import path, include  # ضفنا كلمة include هون

urlpatterns = [
    path('admin/', admin.site.urls), # هاد رابط لوحة التحكم اللي دخلنا عليها قبل شوي
    path('', include('athletes.urls')), # هاد السطر بيوجه أي زائر للصفحة الرئيسية تبعنا
]