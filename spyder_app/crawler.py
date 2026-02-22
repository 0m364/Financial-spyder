import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from .analyzer import SentimentAnalyzer

class WebCrawler:
    def __init__(self, start_url, max_depth=2, max_pages=10):
        self.start_url = start_url
        self.start_url_parsed = urlparse(start_url)
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited = set()
        self.page_count = 0
        self.data = []
        self.corporate_profile = ""
        self.sentiment_scores = []
        self.sentiment_analyzer = SentimentAnalyzer()
        self.factors = {
            'Geopolitical': 0,
            'Environmental': 0,
            'Count_Geo': 0,
            'Count_Env': 0
        }

    def crawl(self):
        queue = [(self.start_url, 0)]

        while queue and self.page_count < self.max_pages:
            url, depth = queue.pop(0)

            if url in self.visited:
                continue

            if depth > self.max_depth:
                continue

            print(f"Crawling: {url} (Depth: {depth})")
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                self.visited.add(url)
                self.page_count += 1

                soup = BeautifulSoup(response.content, 'html.parser')
                self.extract_data(soup, url)

                if depth < self.max_depth:
                    for link in soup.find_all('a', href=True):
                        next_url = urljoin(url, link['href'])
                        parsed_next = urlparse(next_url)

                        if parsed_next.scheme in ['http', 'https'] and parsed_next.netloc == self.start_url_parsed.netloc:
                            if next_url not in self.visited:
                                queue.append((next_url, depth + 1))

                time.sleep(1)

            except requests.RequestException as e:
                print(f"Error crawling {url}: {e}")

    def extract_data(self, soup, url):
        headlines = soup.find_all(['h1', 'h2', 'h3'])
        for headline in headlines:
            text = headline.get_text(strip=True)
            if text:
                sentiment = self.sentiment_analyzer.analyze(text)
                self.sentiment_scores.append(sentiment)

                # Tag factors
                text_lower = text.lower()
                tags = []
                if any(w in text_lower for w in ['war', 'election', 'government', 'policy', 'china', 'usa', 'trade', 'sanction', 'treaty']):
                    tags.append('Geopolitical')
                    self.factors['Geopolitical'] += sentiment
                    self.factors['Count_Geo'] += 1

                if any(w in text_lower for w in ['climate', 'carbon', 'energy', 'oil', 'green', 'sustainable', 'disaster', 'emission']):
                    tags.append('Environmental')
                    self.factors['Environmental'] += sentiment
                    self.factors['Count_Env'] += 1

                self.data.append({
                    'Headline': text,
                    'Sentiment': sentiment,
                    'URL': url,
                    'Tags': tags
                })

        if not self.corporate_profile:
            profile_candidates = [
                soup.find('div', {'class': 'corporate-profile'}),
                soup.find('div', {'id': 'company-profile'}),
                soup.find('div', class_=lambda x: x and 'profile' in x.lower()),
                soup.find('section', class_=lambda x: x and 'about' in x.lower())
            ]
            for candidate in profile_candidates:
                if candidate:
                    self.corporate_profile = candidate.get_text(strip=True)
                    break
