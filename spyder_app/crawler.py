import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import socket
import ipaddress
import re
from .analyzer import TextBlobSentimentAnalyzer


def is_safe_url(url):
    """
    Checks if a URL is safe to crawl by resolving its hostname and checking
    if any of the resolved IP addresses are private, loopback, or link-local.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Resolve hostname (supports IPv4 and IPv6)
        addrinfo = socket.getaddrinfo(hostname, None)

        for result in addrinfo:
            ip_addr = result[4][0]
            ip = ipaddress.ip_address(ip_addr)

            # Check if any resolved IP is private, loopback, link-local, multicast, unspecified, or reserved
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_multicast
                or ip.is_unspecified
                or ip.is_reserved
            ):
                return False

        return True
    except (ValueError, socket.error):
        return False


class WebCrawler:
    GEOPOLITICAL_KEYWORDS = [
        "war",
        "election",
        "government",
        "policy",
        "china",
        "usa",
        "trade",
        "sanction",
        "treaty",
        "famine",
        "human movement",
        "global catastrophe",
        "catastrophe",
        "trends",
    ]
    ENVIRONMENTAL_KEYWORDS = [
        "climate",
        "carbon",
        "energy",
        "oil",
        "green",
        "sustainable",
        "disaster",
        "emission",
    ]

    GEOPOLITICAL_RE = re.compile(r"\b(" + "|".join(re.escape(kw) for kw in GEOPOLITICAL_KEYWORDS) + r")\b", flags=re.IGNORECASE)
    ENVIRONMENTAL_RE = re.compile(r"\b(" + "|".join(re.escape(kw) for kw in ENVIRONMENTAL_KEYWORDS) + r")\b", flags=re.IGNORECASE)

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
        self.sentiment_analyzer = TextBlobSentimentAnalyzer()
        self.factors = {
            "Geopolitical": 0,
            "Environmental": 0,
            "Count_Geo": 0,
            "Count_Env": 0,
        }

    def crawl(self):
        queue = [(self.start_url, 0)]

        while queue and self.page_count < self.max_pages:
            url, depth = queue.pop(0)

            if url in self.visited:
                continue

            if depth > self.max_depth:
                continue

            if not is_safe_url(url):
                print(f"Skipping unsafe URL: {url}")
                continue

            print(f"Crawling: {url} (Depth: {depth})")
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                # Avoid SSRF redirect bypass by disabling auto redirects
                response = requests.get(
                    url, headers=headers, timeout=10, allow_redirects=False, stream=True
                )

                # Manually handle redirects securely
                redirect_count = 0
                while response.is_redirect and redirect_count < 5:
                    next_url = response.headers.get("Location")
                    next_url = urljoin(url, next_url)

                    response.close()  # Close previous response
                    if not is_safe_url(next_url):
                        print(f"Skipping unsafe redirect URL: {next_url}")
                        break

                    response = requests.get(
                        next_url,
                        headers=headers,
                        timeout=10,
                        allow_redirects=False,
                        stream=True,
                    )
                    redirect_count += 1

                if response.is_redirect:
                    response.close()
                    continue

                with response:
                    response.raise_for_status()

                    content_type = response.headers.get("Content-Type", "")
                    if "text/html" not in content_type:
                        print(f"Skipping {url}: Unsupported Content-Type {content_type}")
                        continue

                    content_chunks = []
                    downloaded_size = 0
                    max_size = 10 * 1024 * 1024  # 10 MB

                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            downloaded_size += len(chunk)
                            if downloaded_size > max_size:
                                print(f"Skipping {url}: Response exceeded 10MB limit.")
                                content_chunks = None
                                break
                            content_chunks.append(chunk)

                if content_chunks is None:
                    self.visited.add(url)
                    continue

                self.visited.add(url)
                self.page_count += 1

                soup = BeautifulSoup(b"".join(content_chunks), "html.parser")
                self.extract_data(soup, url)

                if depth < self.max_depth:
                    for link in soup.find_all("a", href=True):
                        next_url = urljoin(url, link["href"])
                        parsed_next = urlparse(next_url)

                        if (
                            parsed_next.scheme in ["http", "https"]
                            and parsed_next.netloc == self.start_url_parsed.netloc
                        ):
                            if next_url not in self.visited:
                                queue.append((next_url, depth + 1))

                time.sleep(1)

            except requests.RequestException as e:
                print(f"Error crawling {url}: {e}")

    def crawl_current_events(self):
        print("Crawling current events for macro-sentiment analysis...")
        # Scrape a generic news site for current events
        news_url = "https://www.reuters.com/world/"  # Use Reuters World News as a proxy

        if not is_safe_url(news_url):
            print(f"Skipping unsafe news URL: {news_url}")
            return

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(
                news_url,
                headers=headers,
                timeout=10,
                allow_redirects=False,
                stream=True,
            )

            # Manually handle redirects securely
            redirect_count = 0
            while response.is_redirect and redirect_count < 5:
                next_url = response.headers.get("Location")
                next_url = urljoin(news_url, next_url)

                response.close()  # Close previous response
                if not is_safe_url(next_url):
                    print(f"Skipping unsafe redirect URL: {next_url}")
                    break

                response = requests.get(
                    next_url,
                    headers=headers,
                    timeout=10,
                    allow_redirects=False,
                    stream=True,
                )
                redirect_count += 1

            if response.is_redirect:
                response.close()
                return

            with response:
                response.raise_for_status()

                content_type = response.headers.get("Content-Type", "")
                if "text/html" not in content_type:
                    print(f"Skipping {news_url}: Unsupported Content-Type {content_type}")
                    return

                content_chunks = []
                downloaded_size = 0
                max_size = 10 * 1024 * 1024  # 10 MB

                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        downloaded_size += len(chunk)
                        if downloaded_size > max_size:
                            print(f"Skipping {news_url}: Response exceeded 10MB limit.")
                            content_chunks = None
                            break
                        content_chunks.append(chunk)

            if content_chunks is None:
                return

            soup = BeautifulSoup(b"".join(content_chunks), "html.parser")
            self.extract_data(soup, news_url)

        except requests.RequestException as e:
            print(f"Error crawling current events {news_url}: {e}")

    def extract_data(self, soup, url):
        headlines = soup.find_all(["h1", "h2", "h3"])
        for headline in headlines:
            text = headline.get_text(strip=True)
            if text:
                sentiment = self.sentiment_analyzer.analyze(text)
                self.sentiment_scores.append(sentiment)

                # Tag factors
                text_lower = text.lower()
                tags = []
                if self.GEOPOLITICAL_RE.search(text_lower):
                    tags.append("Geopolitical")
                    self.factors["Geopolitical"] += sentiment
                    self.factors["Count_Geo"] += 1

                if self.ENVIRONMENTAL_RE.search(text_lower):
                    tags.append("Environmental")
                    self.factors["Environmental"] += sentiment
                    self.factors["Count_Env"] += 1

                self.data.append(
                    {"Headline": text, "Sentiment": sentiment, "URL": url, "Tags": tags}
                )

        if not self.corporate_profile:
            profile_candidates = [
                soup.find("div", {"class": "corporate-profile"}),
                soup.find("div", {"id": "company-profile"}),
                soup.find("div", class_=lambda x: x and "profile" in x.lower()),
                soup.find("section", class_=lambda x: x and "about" in x.lower()),
            ]
            for candidate in profile_candidates:
                if candidate:
                    self.corporate_profile = candidate.get_text(strip=True)
                    break
