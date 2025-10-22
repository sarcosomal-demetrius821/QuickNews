#!/usr/bin/env python3
"""
Populate database with news from all categories
Run this after setting up the new system
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoNews.settings')
django.setup()

from news.scraper import NewsScraper

def populate_all():
    """Scrape all categories in both languages"""
    scraper = NewsScraper()

    categories = [
        'general', 'business', 'national', 'sports', 'world',
        'politics', 'technology', 'startup', 'entertainment', 'miscellaneous'
    ]

    print("🚀 Populating database with news...")
    print("=" * 60)

    # English news
    print("\n📰 Scraping English News...")
    for category in categories:
        try:
            count = scraper.fetch_and_save(category, 'en', limit=15)
            print(f"   ✅ {category.title()}: {count} articles")
        except Exception as e:
            print(f"   ❌ {category.title()}: Error - {e}")

    # Hindi news
    print("\n📰 Scraping Hindi News...")
    for category in categories:
        try:
            count = scraper.fetch_and_save(category, 'hi', limit=15)
            print(f"   ✅ {category.title()}: {count} articles")
        except Exception as e:
            print(f"   ❌ {category.title()}: Error - {e}")

    # Show stats
    from news.models import Headline
    total = Headline.objects.count()

    print("\n" + "=" * 60)
    print(f"✅ Complete! Database now has {total} articles")
    print("\n💡 Next: python3 manage.py runserver")
    print("   Then visit: http://127.0.0.1:8000/")

if __name__ == "__main__":
    populate_all()
