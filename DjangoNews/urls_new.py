"""
Clean URL Configuration - replaces messy old urls.py with 20+ duplicates
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('news.urls_new')),
]
