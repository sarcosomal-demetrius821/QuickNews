"""
Consolidated news scraper module
Replaces the old getnews structure with a single, maintainable scraper
"""
import requests
import time
from bs4 import BeautifulSoup
from django.core.cache import cache
from .models import Headline
import logging

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class NewsScraperError(Exception):
    """Custom exception for scraping errors"""
    pass


class NewsScraper:
    """
    Unified news scraper for Inshorts.com
    Supports multiple categories and languages
    """

    BASE_URL_EN = "https://inshorts.com/en/read"
    BASE_URL_HI = "https://inshorts.com/hi/read"

    # CSS selectors for Inshorts.com
    ARTICLE_CONTAINER = "div.PmX01nT74iM8UNAIENsC"
    TITLE_CLASS = "span.ddVzQcwl2yPlFt4fteIE"
    IMAGE_CONTAINER = "div.r_CK6OaFsecGqhiNxLQR"
    CONTENT_CLASS = "div.KkupEonoVHxNv4A_D7UG"
    DATE_CLASS = "date"

    def __init__(self, timeout=30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_url(self, category, language):
        """Construct the scraping URL"""
        base_url = self.BASE_URL_HI if language == 'hi' else self.BASE_URL_EN

        if category == 'general':
            return base_url
        else:
            # Map 'national' to 'national' for URL
            url_category = category if category != 'national' else 'national'
            return f"{base_url}/{url_category}"

    def extract_image_url(self, article):
        """Extract image URL from article element"""
        try:
            image_div = article.find('div', class_='r_CK6OaFsecGqhiNxLQR')
            if image_div and image_div.find('div'):
                style_attr = image_div.find('div').get('style', '')
                if 'url(' in style_attr:
                    return style_attr.split('url(')[1][:-2]
        except Exception as e:
            logger.debug(f"Image extraction failed: {e}")
        return ""

    def parse_article(self, article, category, language, index=0):
        """Parse a single article element"""
        try:
            # Extract title
            title_element = article.find('span', attrs={"class": "ddVzQcwl2yPlFt4fteIE"})
            title = title_element.text if title_element else "No title available"

            # Extract image
            img = self.extract_image_url(article)

            # Extract content
            content_element = article.find('div', attrs={"class": "KkupEonoVHxNv4A_D7UG"})
            content = content_element.text if content_element else "No content available"

            # Extract date
            date_element = article.find(class_='date')
            date = date_element.text if date_element else ""

            # Extract URL (read more link)
            url = ""
            read_more = article.find('a', text='read more')
            if read_more and read_more.get('href'):
                url = read_more['href']

            return {
                'title': title,
                'content': content,
                'img': img,
                'date': date,
                'url': url or f"https://inshorts.com",
                'category': category,
                'language': language,
                'leaning': 'right' if index % 2 == 0 else 'left',  # Alternate for better distribution
            }
        except Exception as e:
            logger.error(f"Failed to parse article: {e}")
            return None

    def scrape_with_selenium(self, category='general', language='en', limit=200, load_more_clicks=10):
        """
        Scrape news using Selenium to handle dynamic "Load More" button

        Args:
            category: News category
            language: Language code
            limit: Maximum articles to scrape
            load_more_clicks: Number of times to click "Load More"

        Returns:
            List of article dictionaries
        """
        url = self.get_url(category, language)

        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')  # New headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--single-process')  # Prevents crashes
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        driver = None
        try:
            logger.info(f"Starting Selenium scraper for {url}")

            # Initialize Chrome driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(url)

            # Wait for initial articles to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "PmX01nT74iM8UNAIENsC"))
            )

            # Click "Load More" button multiple times
            for i in range(load_more_clicks):
                try:
                    # Find and click the Load More button
                    load_more_btn = driver.find_element(By.CLASS_NAME, "QMXJlc3R5MMJjDGSV4Jd")

                    # Scroll to button
                    driver.execute_script("arguments[0].scrollIntoView(true);", load_more_btn)
                    time.sleep(1)

                    # Click the button
                    load_more_btn.click()
                    logger.info(f"Clicked Load More button ({i+1}/{load_more_clicks})")

                    # Wait for new articles to load
                    time.sleep(2)

                except (NoSuchElementException, TimeoutException):
                    logger.info(f"Load More button not found after {i} clicks - reached end")
                    break
                except Exception as e:
                    logger.warning(f"Error clicking Load More button: {e}")
                    break

            # Get page source and parse with BeautifulSoup
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            articles = soup.find_all('div', attrs={"class": "PmX01nT74iM8UNAIENsC"})

            if not articles:
                logger.warning(f"No articles found for {category}/{language}")
                return []

            parsed_articles = []
            for index, article in enumerate(articles[:limit]):
                parsed = self.parse_article(article, category, language, index)
                if parsed:
                    parsed_articles.append(parsed)

            logger.info(f"Successfully scraped {len(parsed_articles)} articles with Selenium")
            return parsed_articles

        except Exception as e:
            logger.error(f"Selenium scraping failed: {e}")
            raise NewsScraperError(f"Selenium scraping error: {e}")
        finally:
            if driver:
                driver.quit()

    def scrape_category(self, category='general', language='en', limit=25):
        """
        Scrape news for a specific category and language

        Args:
            category: News category (general, business, sports, etc.)
            language: Language code ('en' or 'hi')
            limit: Maximum number of articles to scrape

        Returns:
            List of article dictionaries
        """
        url = self.get_url(category, language)
        cache_key = f"news_{category}_{language}"

        # Check cache first
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Returning cached data for {category}/{language}")
            return cached_data

        # Note: Selenium support available but disabled due to Chrome headless issues
        # Uncomment below to enable dynamic scraping with Load More button
        # if limit > 25:
        #     logger.info(f"Using Selenium for large limit ({limit})")
        #     articles = self.scrape_with_selenium(category, language, limit, load_more_clicks=15)
        #     cache.set(cache_key, articles, 1800)
        #     return articles

        try:
            logger.info(f"Scraping {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')
            articles = soup.find_all('div', attrs={"class": "PmX01nT74iM8UNAIENsC"})

            if not articles:
                logger.warning(f"No articles found for {category}/{language}")
                return []

            parsed_articles = []
            for index, article in enumerate(articles[:limit]):
                parsed = self.parse_article(article, category, language, index)
                if parsed:
                    parsed_articles.append(parsed)

            # Cache for 30 minutes
            cache.set(cache_key, parsed_articles, 1800)

            logger.info(f"Successfully scraped {len(parsed_articles)} articles")
            return parsed_articles

        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            raise NewsScraperError(f"Failed to fetch news: {e}")
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise NewsScraperError(f"Scraping error: {e}")

    def save_to_database(self, articles, replace=False):
        """
        Save scraped articles to database

        Args:
            articles: List of article dictionaries
            replace: If True, delete existing articles for this category/language
        """
        if not articles:
            return 0

        # Get category and language from first article
        category = articles[0].get('category')
        language = articles[0].get('language')

        if replace:
            # Delete old articles for this category/language
            deleted = Headline.objects.filter(
                category=category,
                language=language
            ).delete()
            logger.info(f"Deleted {deleted[0]} old articles for {category}/{language}")

        # Filter out articles that already exist (duplicate title check)
        new_articles = []
        for article in articles:
            if not Headline.objects.filter(title=article['title']).exists():
                new_articles.append(article)
            else:
                logger.debug(f"Skipping duplicate: {article['title'][:50]}...")

        if not new_articles:
            logger.info(f"No new articles to save for {category}/{language} (all duplicates)")
            return 0

        # Create new headlines
        headlines = [Headline(**article) for article in new_articles]
        created = Headline.objects.bulk_create(headlines, ignore_conflicts=True)

        logger.info(f"Saved {len(created)} new articles to database (skipped {len(articles) - len(new_articles)} duplicates)")
        return len(created)

    def fetch_and_save(self, category='general', language='en', limit=25, replace=True):
        """
        Convenience method to scrape and save in one call

        Args:
            category: News category
            language: Language code
            limit: Max articles to scrape
            replace: Whether to replace existing articles

        Returns:
            Number of articles saved
        """
        articles = self.scrape_category(category, language, limit)
        return self.save_to_database(articles, replace=replace)


def get_news(category='general', language='en', limit=25):
    """
    Simple function to get news - maintains backward compatibility
    """
    scraper = NewsScraper()
    return scraper.fetch_and_save(category, language, limit)
