from gettext import find
from ...models import Headline
from bs4 import BeautifulSoup
import requests

def scrape_hindi_category(url, category, per_site=25):
    """
    Generic scraping function for Hindi news to prevent code duplication and ensure consistent duplicate handling
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
                    headline.language = 'hi'

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
                    print(f"Error processing Hindi {category} article: {e}")
                    continue
    except Exception as e:
        print(f"Error fetching Hindi {category} from {url}: {e}")


def hindi_getcbs(per_site):
    scrape_hindi_category('https://inshorts.com/hi/read', 'general', per_site)


def hindi_business(per_site):
    scrape_hindi_category('https://www.inshorts.com/hi/read/business', 'business', per_site)


def hindi_sports(per_site):
    scrape_hindi_category('https://inshorts.com/hi/read/sports', 'sports', per_site)


def hindi_indin(per_site):
    scrape_hindi_category('https://inshorts.com/hi/read/national', 'national', per_site)


def hindi_world(per_site):
    scrape_hindi_category('https://inshorts.com/hi/read/world', 'world', per_site)


def hindi_politics(per_site):
    scrape_hindi_category('https://inshorts.com/hi/read/politics', 'politics', per_site)


def hindi_technology(per_site):
    scrape_hindi_category('https://inshorts.com/hi/read/technology', 'technology', per_site)


def hindi_startup(per_site):
    scrape_hindi_category('https://inshorts.com/hi/read/startup', 'startup', per_site)


def hindi_entertainment(per_site):
    scrape_hindi_category('https://inshorts.com/hi/read/entertainment', 'entertainment', per_site)


def hindi_miscellaneous(per_site):
    scrape_hindi_category('https://inshorts.com/hi/read/miscellaneous', 'miscellaneous', per_site)
