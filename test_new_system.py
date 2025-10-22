#!/usr/bin/env python3
"""
Quick test script for the new modernized system
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoNews.settings')
django.setup()

from news.scraper import NewsScraper
from news.models import Headline

def test_scraper():
    """Test the new scraper"""
    print("🔍 Testing New Scraper...")
    print("-" * 50)

    scraper = NewsScraper()

    # Test English general news
    print("\n1️⃣ Scraping English General News...")
    try:
        count = scraper.fetch_and_save('general', 'en', limit=10)
        print(f"   ✅ Scraped and saved {count} articles")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test Hindi business news
    print("\n2️⃣ Scraping Hindi Business News...")
    try:
        count = scraper.fetch_and_save('business', 'hi', limit=10)
        print(f"   ✅ Scraped and saved {count} articles")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test cache
    print("\n3️⃣ Testing Cache (should be instant)...")
    try:
        import time
        start = time.time()
        articles = scraper.scrape_category('general', 'en')
        elapsed = time.time() - start
        print(f"   ✅ Retrieved {len(articles)} articles in {elapsed:.3f}s (cached!)")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def show_stats():
    """Show database statistics"""
    print("\n" + "=" * 50)
    print("📊 Database Statistics")
    print("=" * 50)

    total = Headline.objects.count()
    print(f"\nTotal Headlines: {total}")

    if total > 0:
        # By language
        print("\n📰 By Language:")
        for lang in ['en', 'hi']:
            count = Headline.objects.filter(language=lang).count()
            lang_name = 'English' if lang == 'en' else 'Hindi'
            print(f"   {lang_name}: {count}")

        # By category
        print("\n📂 By Category:")
        categories = Headline.objects.values_list('category', flat=True).distinct()
        for cat in categories:
            count = Headline.objects.filter(category=cat).count()
            print(f"   {cat.title()}: {count}")

        # Recent articles
        print("\n🕐 Recent Articles:")
        recent = Headline.objects.order_by('-created_at')[:5]
        for i, article in enumerate(recent, 1):
            print(f"   {i}. [{article.category}] {article.title[:60]}...")

    print("\n" + "=" * 50)

if __name__ == "__main__":
    print("🚀 Django News - New System Test")
    print("=" * 50)

    # Test scraper
    test_scraper()

    # Show stats
    show_stats()

    print("\n✅ Test Complete!")
    print("\n💡 Next Steps:")
    print("   1. Update DjangoNews/urls.py to use 'news.urls_new'")
    print("   2. Update views_new.py template_name to 'news/news_modern.html'")
    print("   3. Run: python3 manage.py runserver")
    print("   4. Visit: http://127.0.0.1:8000/")
    print("\n🎨 Your modern news app awaits!\n")
