import feedparser
import requests
from bs4 import BeautifulSoup
import urllib.parse
import base64

def decode_google_news_url(url):
    """
    Attempts to resolve the actual news URL from a Google News redirect link.
    """
    try:
        # 1. Simple Request Follow (Works 80% of the time)
        response = requests.head(url, allow_redirects=True, timeout=5)
        if "news.google.com" not in response.url:
            return response.url
            
        # 2. If that fails, scrape the redirect page
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for the clickable link in the redirect page
        link_tag = soup.find('a', href=True)
        if link_tag:
            return link_tag['href']
            
    except:
        pass
        
    return url # Return original if decode fails

def get_trending_news(region="IN"):
    feeds = {
        "IN": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
        "US": "https://www.cbsnews.com/latest/rss/main",
        "WORLD": "http://feeds.bbci.co.uk/news/world/rss.xml"
    }
    
    selected_url = feeds.get(region, feeds["IN"])
    
    try:
        feed = feedparser.parse(selected_url)
        trends = []
        for entry in feed.entries[:8]:
            trends.append({
                "title": entry.title,
                "link": entry.link
            })
        return trends
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return []

def get_social_trends(region="IN"):
    urls = {
        "IN": "https://trends24.in/india/",
        "US": "https://trends24.in/united-states/",
        "WORLD": "https://trends24.in/"
    }
    
    url = urls.get(region, urls["IN"])
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        trend_list = soup.find('ol', class_='trend-card__list')
        hashtags = []
        if trend_list:
            for li in trend_list.find_all('li')[:10]:
                hashtags.append(li.find('a').get_text())
        return hashtags
    except Exception as e:
        print(f"❌ Error fetching hashtags: {e}")
        return []

def find_news_url_for_tag(hashtag):
    """
    Finds a news article for a hashtag and DECODES the link.
    """
    encoded_tag = urllib.parse.quote(hashtag)
    rss_url = f"https://news.google.com/rss/search?q={encoded_tag}&hl=en-IN&gl=IN&ceid=IN:en"
    
    try:
        feed = feedparser.parse(rss_url)
        if feed.entries:
            raw_link = feed.entries[0].link
           
            clean_link = decode_google_news_url(raw_link)
            return clean_link
    except:
        pass
    
    return None