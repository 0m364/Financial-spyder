import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from fpdf import FPDF
from textblob import TextBlob
import time
from urllib.parse import urljoin, urlparse

class FinancialSpyder:
    def __init__(self, start_url, csv_file, pdf_file, max_depth=2, max_pages=10):
        self.start_url = start_url
        self.csv_file = csv_file
        self.pdf_file = pdf_file
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited = set()
        self.data = []
        self.corporate_profile = ""
        self.sentiment_scores = []
        self.page_count = 0

    def crawl(self):
        queue = [(self.start_url, 0)]  # (url, depth)

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

                # Find links for next depth
                if depth < self.max_depth:
                    for link in soup.find_all('a', href=True):
                        next_url = urljoin(url, link['href'])
                        # Only follow http/https links and stay on same domain (optional, but good for focus)
                        parsed_start = urlparse(self.start_url)
                        parsed_next = urlparse(next_url)

                        if parsed_next.scheme in ['http', 'https'] and parsed_next.netloc == parsed_start.netloc:
                            if next_url not in self.visited:
                                queue.append((next_url, depth + 1))

                # Be polite
                time.sleep(1)

            except requests.RequestException as e:
                print(f"Error crawling {url}: {e}")

    def extract_data(self, soup, url):
        # Extract headlines
        headlines = soup.find_all(['h1', 'h2', 'h3'])
        for headline in headlines:
            text = headline.get_text(strip=True)
            if text:
                sentiment = self.analyze_sentiment(text)
                self.sentiment_scores.append(sentiment)
                self.data.append({
                    'Headline': text,
                    'Sentiment': sentiment,
                    'URL': url
                })

        # Extract corporate profile (improved selector logic could be added here)
        # Trying multiple common classes for profile/about sections
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

    def analyze_sentiment(self, text):
        blob = TextBlob(text)
        return blob.sentiment.polarity

    def save_csv(self):
        if not self.data:
            print("No data to save to CSV.")
            return

        df = pd.DataFrame(self.data)
        df.to_csv(self.csv_file, index=False)
        print(f"Data saved to {self.csv_file}")

    def generate_report(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="Financial Market Analysis Report", ln=True, align='C')
        pdf.ln(10)

        # Disclaimer
        pdf.set_font("Arial", 'I', 10)
        pdf.set_text_color(255, 0, 0)
        disclaimer = "DISCLAIMER: This tool is for informational purposes only and does not constitute financial advice. The market predictions are based on simple sentiment analysis and should not be used for trading decisions."
        pdf.multi_cell(0, 5, txt=disclaimer)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(10)

        # Summary
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Crawl Summary", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"Pages Crawled: {self.page_count}", ln=True)
        pdf.cell(200, 10, txt=f"Headlines Extracted: {len(self.data)}", ln=True)

        avg_sentiment = sum(self.sentiment_scores) / len(self.sentiment_scores) if self.sentiment_scores else 0
        pdf.cell(200, 10, txt=f"Average Sentiment Score: {avg_sentiment:.2f}", ln=True)

        outlook = "NEUTRAL"
        if avg_sentiment > 0.1:
            outlook = "BULLISH"
        elif avg_sentiment < -0.1:
            outlook = "BEARISH"

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"Market Outlook: {outlook}", ln=True)
        pdf.ln(10)

        # Corporate Profile
        if self.corporate_profile:
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, txt="Corporate Profile", ln=True)
            pdf.set_font("Arial", size=10)
            # Handle unicode characters that fpdf might struggle with
            safe_text = self.corporate_profile.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 5, txt=safe_text)
            pdf.ln(10)

        # Top Positive/Negative Headlines
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Top Headlines", ln=True)
        pdf.set_font("Arial", size=10)

        sorted_data = sorted(self.data, key=lambda x: x['Sentiment'], reverse=True)
        top_positive = sorted_data[:5]
        top_negative = sorted_data[-5:]

        pdf.cell(200, 10, txt="Most Positive:", ln=True)
        for item in top_positive:
            txt = f"{item['Headline']} ({item['Sentiment']:.2f})"
            pdf.multi_cell(0, 5, txt=txt.encode('latin-1', 'replace').decode('latin-1'))

        pdf.ln(5)
        pdf.cell(200, 10, txt="Most Negative:", ln=True)
        for item in top_negative:
            txt = f"{item['Headline']} ({item['Sentiment']:.2f})"
            pdf.multi_cell(0, 5, txt=txt.encode('latin-1', 'replace').decode('latin-1'))

        pdf.output(self.pdf_file)
        print(f"Report saved to {self.pdf_file}")

    def run(self):
        print("Starting Financial Spyder...")
        self.crawl()
        self.save_csv()
        self.generate_report()
        print("Done.")

if __name__ == "__main__":
    # Example usage
    # You can change the URL to a financial news site or company page
    spider = FinancialSpyder(
        start_url='https://www.example.com',
        csv_file='financial_data.csv',
        pdf_file='market_report.pdf',
        max_depth=2,
        max_pages=5
    )
    spider.run()
