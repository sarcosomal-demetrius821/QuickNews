# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django-based news aggregation application that scrapes news articles from Inshorts.com. Originally built in 2021 as a college project, it supports both English and Hindi news across multiple categories.

## Development Setup

### Virtual Environment
```bash
# Activate virtual environment
source env/bin/activate

# Install dependencies (from pip freeze)
pip install Django==5.2.7 beautifulsoup4==4.14.2 bs4==0.0.2 requests==2.32.5 lxml==6.0.2
```

### Database Operations
```bash
# Run migrations
python3 manage.py makemigrations
python3 manage.py migrate

# Create superuser (for admin access)
python3 manage.py createsuperuser
```

### Running the Application
```bash
# Start development server
python3 manage.py runserver

# Access points:
# - English news: http://127.0.0.1:8000/
# - Hindi news: http://127.0.0.1:8000/hindi/
# - Admin panel: http://127.0.0.1:8000/admin/
```

## Architecture

### Project Structure
- **DjangoNews/** - Main Django project configuration
  - `settings.py` - Project settings (uses SQLite, DEBUG=True, configured for Vercel deployment)
  - `urls.py` - Root URL configuration (all routes delegated to news app)
- **news/** - Core news application
  - `models.py` - Single `Headline` model storing scraped articles
  - `views.py` - 20 view functions (10 English + 10 Hindi categories)
  - `urls.py` - URL patterns for all categories
  - `getnews/` - Web scraping module
    - `getnews.py` - Orchestrates scraping for each category
    - `news_sites/getcbs.py` - English news scrapers for Inshorts.com
    - `news_sites/gethindi.py` - Hindi news scrapers for Inshorts.com
- **templates/** - Django templates
  - `news/` - English news templates
  - `hindinews/` - Hindi news templates
  - `base.html` - Base template
- **static/** - CSS, JavaScript, and image assets

### Data Flow
1. User visits a category URL (e.g., `/business/`, `/hindi/sports/`)
2. Corresponding view function calls appropriate scraping function from `getnews/`
3. Scraper fetches HTML from Inshorts.com for that category
4. BeautifulSoup parses HTML and extracts article data (title, image, content, date)
5. All existing headlines are deleted from database (`Headline.objects.all().delete()`)
6. New headlines are saved to database with `leaning='left'` and `leaning='right'` logic
7. View retrieves headlines, selects preview articles (3 left + 3 right leaning with images)
8. Template renders news articles

### Database Model
```python
class Headline(models.Model):
    leaning = models.TextField()  # 'left' or 'right'
    title = models.TextField()
    img = models.URLField(max_length=1000, null=True, blank=True)
    content = models.TextField()
    date = models.TextField(null=True)
    url = models.URLField(max_length=1000)
```

### Web Scraping Details
- **Target site**: Inshorts.com (English: `/en/read/`, Hindi: `/hi/read/`)
- **Key HTML classes** (subject to change):
  - Article container: `PmX01nT74iM8UNAIENsC`
  - Title: `ddVzQcwl2yPlFt4fteIE`
  - Image container: `r_CK6OaFsecGqhiNxLQR`
  - Content: `KkupEonoVHxNv4A_D7UG`
  - Date: `date`
- **Error handling**: `getcbs()` function has comprehensive error handling; other category functions need similar improvements
- **Note**: Each view function deletes ALL headlines before scraping, so only one category's news is stored at a time

### Categories Supported
English: General, Business, National (indin), Sports, World, Politics, Entertainment, Miscellaneous, Startup, Technology
Hindi: Same 10 categories with Hindi content

## Development Practices

### When Working on Views
- Each category has its own view function (`shownews`, `shownews1`, etc. for English; `shownewshindi0`, etc. for Hindi)
- All views follow identical pattern: call scraper → query database → prepare preview list → render template
- Preview selection logic: 3 'right' + 3 'left' leaning articles with images, shuffled randomly

### When Working on Scrapers
- Follow error handling pattern from `getcbs()` function (lines 14-47 in `news/getnews/news_sites/getcbs.py`)
- Always check for None before accessing element attributes
- Use try-except blocks to prevent scraping failures from crashing
- Test against live Inshorts.com site as HTML structure may change

### URL Configuration Note
- `DjangoNews/urls.py` has duplicate `path('', include('news.urls'))` entries (lines 21-40) - these are redundant but harmless

### Testing
```bash
# Test specific category by visiting URL
# Example: http://127.0.0.1:8000/technology/

# Check Django admin to verify scraped data
# http://127.0.0.1:8000/admin/
```

## Known Issues & Technical Debt
- Settings contains exposed SECRET_KEY (needs environment variable)
- Database is wiped on each category view (consider category-specific filtering instead)
- Significant code duplication across view functions (20 nearly identical functions)
- Most scraper functions lack error handling present in `getcbs()`
- URL configuration has unnecessary duplicates
- No requirements.txt file (dependencies must be inferred from pip freeze)
- Vercel deployment configuration present but not documented

## Future Modernization Plans
According to README, planned improvements include modern UI/UX, optimized code, new features, better mobile support, and performance improvements in a new repository.
