from gettext import find
from ...models import Headline
from bs4 import BeautifulSoup
import requests

def scrape_category(url, category, language='en', per_site=25):
    """
    Generic scraping function to prevent code duplication and ensure consistent duplicate handling
    """
    try:
        html = requests.get(url).text
        soup = BeautifulSoup(html, 'lxml')
        article_list = soup.find_all('div', attrs={"class": "PmX01nT74iM8UNAIENsC"})

        count = 0
        for art in article_list:
            if count < per_site:
                try:
                    # Get title
                    title_element = art.find('span', attrs={"class": "ddVzQcwl2yPlFt4fteIE"})
                    title = title_element.text if title_element else "No title available"

                    # Skip if duplicate title already exists
                    if Headline.objects.filter(title=title).exists():
                        continue

                    headline = Headline()
                    headline.title = title
                    headline.leaning = 'left' if count % 2 == 0 else 'right'
                    headline.category = category
                    headline.language = language

                    # Get image
                    image_div = art.find('div', class_='r_CK6OaFsecGqhiNxLQR')
                    if image_div and image_div.find('div'):
                        style_attr = image_div.find('div').get('style', '')
                        if 'url(' in style_attr:
                            headline.img = style_attr.split('url(')[1][:-2]
                        else:
                            headline.img = ""
                    else:
                        headline.img = ""

                    # Get content
                    content_element = art.find('div', attrs={"class": "KkupEonoVHxNv4A_D7UG"})
                    headline.content = content_element.text if content_element else "No content available"

                    # Get date
                    date_element = art.find(class_='date')
                    headline.date = date_element.text if date_element else ""

                    headline.save()
                    count += 1
                except Exception as e:
                    print(f"Error processing {category} article: {e}")
                    continue
    except Exception as e:
        print(f"Error fetching {category} from {url}: {e}")


def getcbs(per_site):
    scrape_category('https://inshorts.com/en/read', 'general', 'en', per_site)


def business(per_site):
    scrape_category('https://www.inshorts.com/en/read/business', 'business', 'en', per_site)


def sports(per_site):
    scrape_category('https://inshorts.com/en/read/sports', 'sports', 'en', per_site)


def indin(per_site):
    scrape_category('https://inshorts.com/en/read/national', 'national', 'en', per_site)


def world(per_site):
    scrape_category('https://inshorts.com/en/read/world', 'world', 'en', per_site)


def politics(per_site):
    scrape_category('https://inshorts.com/en/read/politics', 'politics', 'en', per_site)


def technology(per_site):
    scrape_category('https://inshorts.com/en/read/technology', 'technology', 'en', per_site)


def startup(per_site):
    scrape_category('https://inshorts.com/en/read/startup', 'startup', 'en', per_site)


def entertainment(per_site):
    scrape_category('https://inshorts.com/en/read/entertainment', 'entertainment', 'en', per_site)


def miscellaneous(per_site):
    scrape_category('https://inshorts.com/en/read/miscellaneous', 'miscellaneous', 'en', per_site)
