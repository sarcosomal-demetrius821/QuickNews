"""
Django News - Modern URL Configuration
Clean, optimized URL routing
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('news.urls_new')),  # New modern URLs
]
