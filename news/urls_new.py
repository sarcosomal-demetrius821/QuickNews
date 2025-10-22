"""
Clean URL configuration - replaces messy old urls.py
"""
from django.urls import path
from django.views.generic import RedirectView
from .views_new import NewsListView, load_more_news

app_name = 'news'

urlpatterns = [
    # AJAX endpoint for Load More (must be first to avoid being caught by category pattern)
    path('api/load-more/', load_more_news, name='load_more'),

    # Ignore favicon.ico requests
    path('favicon.ico/', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),

    # English news routes
    path('', NewsListView.as_view(), {'category': 'general', 'language': 'en'}, name='home'),

    # Hindi news routes (MUST come before generic category pattern)
    path('hindi/', NewsListView.as_view(), {'category': 'general', 'language': 'hi'}, name='hindi_home'),
    path('hindi/<str:category>/', NewsListView.as_view(), {'language': 'hi'}, name='hindi_category'),

    # Generic English category routes (catch-all, must be last)
    path('<str:category>/', NewsListView.as_view(), {'language': 'en'}, name='category'),
]
