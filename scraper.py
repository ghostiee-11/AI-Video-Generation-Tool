import requests
from bs4 import BeautifulSoup
import time

def resolve_google_url(url):
    """
    Extracts the actual news URL from a Google News RSS redirect link.
    """
    if "news.google.com" not in url and "google.com/url" not in url:
        return url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Get the redirection page content
        response = requests.get(url, headers=headers, timeout=10)
        
        # Parse the HTML to find the destination link
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Google usually puts the real link in the first <a> tag or a specific class
        # We look for the first valid http link that isn't Google itself
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            # Return the first external link found
            if href.startswith("http") and "google.com" not in href:
                return href
                
        # If standard parsing fails, return the URL (request might have followed a 301)
        return response.url
        
    except Exception as e:
        print(f"   ⚠️ URL Resolution Warning: {e}")
        return url

def scrape_article(url):
    """
    Scrapes the article title and text.
    Includes logic to resolve Google News redirects.
    """
    # 1. RESOLVE REAL URL
    target_url = resolve_google_url(url)
    
    if target_url != url:
        print(f"🔗 Resolving Google Link...\n   Original: {url}\n   Target: {target_url}")
    else:
        print(f"🔗 Scraper Input URL: {url}")

    # Standard Headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }

    try:
        session = requests.Session()
        response = session.get(target_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 2. PARSE CONTENT
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Clean up unwanted tags
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe", "svg"]):
            tag.decompose()

        # 3. EXTRACT TITLE
        title = None
        if soup.find('h1'):
            title = soup.find('h1').get_text().strip()
        elif soup.find('title'):
            title = soup.find('title').get_text().strip()
        
        if not title:
            title = "News Article"

        # 4. EXTRACT TEXT
        paragraphs = soup.find_all('p')
        clean_paragraphs = []
        for p in paragraphs:
            text = p.get_text().strip()
            # Filter out short/empty lines and common footer text
            if len(text.split()) > 6 and "copyright" not in text.lower():
                clean_paragraphs.append(text)
        
        full_text = " ".join(clean_paragraphs)
        
        # Validation
        if len(full_text) < 200:
            print("   ⚠️ Content too short after resolving. Site might block scrapers.")
            return None

        print(f"   ✅ Successfully scraped: {title[:30]}...")
        
        return {
            "title": title,
            "text": full_text[:3500] 
        }

    except Exception as e:
        print(f"❌ Scraping Error: {e}")
        return None