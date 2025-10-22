"""
Refactored views - replaces 20 duplicate functions with clean, DRY code
"""
from django.views.generic import ListView
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Headline
from .scraper import NewsScraper
import logging
import random

logger = logging.getLogger(__name__)


def parse_article_date(date_string):
    """
    Parse date string from Inshorts (e.g., 'Monday, 21 October, 2025')
    Returns datetime object for sorting, or current time if parsing fails
    """
    if not date_string:
        return timezone.now()

    try:
        # Format: "Monday, 21 October, 2025"
        parsed = datetime.strptime(date_string, "%A, %d %B, %Y")
        return timezone.make_aware(parsed)
    except:
        try:
            # Alternative format: "21 Oct"
            current_year = datetime.now().year
            parsed = datetime.strptime(f"{date_string} {current_year}", "%d %b %Y")
            return timezone.make_aware(parsed)
        except:
            # If all parsing fails, return current time
            return timezone.now()


class NewsListView(ListView):
    """
    Unified view for all news categories and languages
    Replaces 20 separate view functions
    """
    model = Headline
    template_name = 'news/news.html'
    context_object_name = 'headline_list'
    paginate_by = 25

    def get_category(self):
        """Get category from URL or default to 'general'"""
        return self.kwargs.get('category', 'general')

    def get_language(self):
        """Get language from URL or default to 'en'"""
        return self.kwargs.get('language', 'en')

    def get_queryset(self):
        """Get headlines for the specific category and language"""
        category = self.get_category()
        language = self.get_language()

        # Ignore invalid categories (like favicon.ico)
        valid_categories = ['general', 'business', 'national', 'sports', 'world',
                           'politics', 'technology', 'startup', 'entertainment', 'miscellaneous']
        if category not in valid_categories:
            logger.warning(f"Invalid category requested: {category}")
            return Headline.objects.none()

        # Check if we have recent data in the database
        thirty_minutes_ago = timezone.now() - timedelta(minutes=30)
        existing_articles = Headline.objects.filter(
            category=category,
            language=language,
            created_at__gte=thirty_minutes_ago
        )

        # Only scrape if no recent data exists
        if not existing_articles.exists():
            logger.info(f"No recent data found for {category}/{language}, scraping...")
            try:
                scraper = NewsScraper()
                scraper.fetch_and_save(
                    category=category,
                    language=language,
                    limit=50,  # Realistic limit based on Inshorts initial page load
                    replace=False  # Keep old articles, only add new ones (duplicate prevention in scraper)
                )
            except Exception as e:
                logger.error(f"Scraping failed for {category}/{language}: {e}")
        else:
            logger.info(f"Using cached data from DB for {category}/{language} ({existing_articles.count()} articles)")

        # Return all headlines from database, ordered by publication date (newest first)
        # Sort by created_at as primary (newest articles first), then by id descending for stability
        return Headline.objects.filter(
            category=category,
            language=language
        ).order_by('-created_at', '-id')

    def get_template_names(self):
        """Use different template for Hindi"""
        language = self.get_language()
        if language == 'hi':
            return ['hindinews/news.html']
        return ['news/news.html']

    def get_context_data(self, **kwargs):
        """Add preview headlines to context"""
        context = super().get_context_data(**kwargs)

        headlines = list(context['headline_list'])

        # Sort headlines by publication date (newest first - Oct 21 before Oct 20)
        headlines_sorted = sorted(
            headlines,
            key=lambda h: parse_article_date(h.date),
            reverse=True  # Newest first
        )

        # Update context with sorted headlines
        context['headline_list'] = headlines_sorted

        # Select preview articles (3 left + 3 right with images) from sorted list
        preview = []
        right_count = 0
        left_count = 0

        for headline in headlines_sorted:
            if headline.leaning == 'right' and right_count < 3 and headline.img:
                preview.append(headline)
                right_count += 1
            elif headline.leaning == 'left' and left_count < 3 and headline.img:
                preview.append(headline)
                left_count += 1

            if right_count >= 3 and left_count >= 3:
                break

        random.shuffle(preview)

        context.update({
            'preview': preview,
            'num_headlines': len(headlines_sorted),
            'current_category': self.get_category(),
            'current_language': self.get_language(),
        })

        return context


# Function-based view for backward compatibility
def show_news(request, category='general', language='en'):
    """
    Simple function-based view
    Maps old URLs to new unified view
    """
    view = NewsListView.as_view()
    return view(request, category=category, language=language)


# Convenience functions for specific categories (backward compatibility)
def shownews(request):
    return show_news(request, 'general', 'en')


def shownews_category(request, category):
    return show_news(request, category, 'en')


def shownews_hindi(request, category='general'):
    return show_news(request, category, 'hi')


def load_more_news(request):
    """
    AJAX endpoint for Load More functionality
    Returns JSON with more articles

    IMPORTANT: Initial page shows 25 articles, so load_more must use the same page size
    to avoid duplicates
    """
    category = request.GET.get('category', 'general')
    language = request.GET.get('language', 'en')
    page = int(request.GET.get('page', 1))

    # Get headlines for category and language
    headlines = list(Headline.objects.filter(
        category=category,
        language=language
    ).order_by('-created_at'))

    # Sort by publication date (newest first - Oct 21 before Oct 20)
    headlines_sorted = sorted(
        headlines,
        key=lambda h: parse_article_date(h.date),
        reverse=True
    )

    # MUST match paginate_by in NewsListView (25) to prevent duplicates
    paginator = Paginator(headlines_sorted, 25)

    # Validate page number
    if page < 1:
        page = 1
    elif page > paginator.num_pages:
        # Return empty if beyond available pages
        return JsonResponse({
            'articles': [],
            'has_next': False,
            'next_page': None,
        })

    page_obj = paginator.page(page)

    # Build JSON response
    articles = []
    for headline in page_obj:
        articles.append({
            'title': headline.title,
            'content': headline.content[:150] + '...' if len(headline.content) > 150 else headline.content,
            'img': headline.img or '',
            'url': headline.url or '',  # Add fallback for url
            'date': headline.date or 'Recently',
            'leaning': headline.leaning,
            'language': headline.language,
        })

    return JsonResponse({
        'articles': articles,
        'has_next': page_obj.has_next(),
        'next_page': page + 1 if page_obj.has_next() else None,
        'current_page': page,
        'total_pages': paginator.num_pages,
    })
