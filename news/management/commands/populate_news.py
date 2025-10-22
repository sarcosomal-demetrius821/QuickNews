"""
Management command to populate news database with all categories
Usage: python manage.py populate_news
"""
from django.core.management.base import BaseCommand
from news.scraper import NewsScraper
from news.models import Headline


class Command(BaseCommand):
    help = 'Scrape and populate news for all categories in both English and Hindi'

    def add_arguments(self, parser):
        parser.add_argument(
            '--language',
            type=str,
            choices=['en', 'hi', 'both'],
            default='both',
            help='Language to scrape (en, hi, or both)'
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Specific category to scrape (leave empty for all)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=200,
            help='Maximum articles per category (default: 200)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before scraping'
        )

    def handle(self, *args, **options):
        categories = [
            'general', 'business', 'national', 'sports', 'world',
            'politics', 'entertainment', 'miscellaneous', 'startup', 'technology'
        ]

        # Filter to specific category if provided
        if options['category']:
            if options['category'] in categories:
                categories = [options['category']]
            else:
                self.stdout.write(self.style.ERROR(f"Invalid category: {options['category']}"))
                return

        # Determine languages to scrape
        languages = []
        if options['language'] in ['en', 'both']:
            languages.append('en')
        if options['language'] in ['hi', 'both']:
            languages.append('hi')

        # Clear existing data if requested
        if options['clear']:
            count = Headline.objects.all().count()
            Headline.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {count} existing articles"))

        scraper = NewsScraper()
        total_scraped = 0
        failed = []

        self.stdout.write(self.style.SUCCESS(f"\nStarting news scraping..."))
        self.stdout.write(f"Categories: {len(categories)}")
        self.stdout.write(f"Languages: {', '.join(languages)}")
        self.stdout.write(f"Limit per category: {options['limit']}\n")

        for language in languages:
            lang_name = "English" if language == 'en' else "Hindi"
            self.stdout.write(self.style.HTTP_INFO(f"\n{'='*60}"))
            self.stdout.write(self.style.HTTP_INFO(f"Scraping {lang_name} News"))
            self.stdout.write(self.style.HTTP_INFO(f"{'='*60}"))

            for category in categories:
                try:
                    self.stdout.write(f"\n📰 Scraping {category.upper()} ({lang_name})...", ending='')

                    count = scraper.fetch_and_save(
                        category=category,
                        language=language,
                        limit=options['limit'],
                        replace=True
                    )

                    total_scraped += count
                    self.stdout.write(self.style.SUCCESS(f" ✓ {count} articles"))

                except Exception as e:
                    failed.append(f"{category}/{language}")
                    self.stdout.write(self.style.ERROR(f" ✗ Failed: {str(e)}"))

        # Summary
        self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
        self.stdout.write(self.style.SUCCESS(f"SCRAPING COMPLETE"))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}"))
        self.stdout.write(f"Total articles scraped: {total_scraped}")
        self.stdout.write(f"Total in database: {Headline.objects.count()}")

        if failed:
            self.stdout.write(self.style.WARNING(f"\nFailed categories: {', '.join(failed)}"))
        else:
            self.stdout.write(self.style.SUCCESS("\n✓ All categories scraped successfully!"))
