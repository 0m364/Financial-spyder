import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from fpdf import FPDF
from textblob import TextBlob
import time
from urllib.parse import urljoin, urlparse
import yfinance as yf
import ta
import datetime
import os

class FinancialSpyder:
    def __init__(self, start_url, ticker, csv_file, pdf_file, max_depth=2, max_pages=10):
        self.start_url = start_url
        self.start_url_parsed = urlparse(start_url)
        self.ticker = ticker
        self.csv_file = csv_file
        self.pdf_file = pdf_file
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited = set()
        self.data = []
        self.corporate_profile = ""
        self.sentiment_scores = []
        self.page_count = 0
        self.historical_data = None
        self.technicals = {}

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
                        # Only follow http/https links and stay on same domain
                        parsed_next = urlparse(next_url)

                        if parsed_next.scheme in ['http', 'https'] and parsed_next.netloc == self.start_url_parsed.netloc:
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

        # Extract corporate profile
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

    def get_historical_data(self):
        print(f"Fetching historical data for {self.ticker}...")
        try:
            ticker_obj = yf.Ticker(self.ticker)
            # "every move the stock market ever made" -> period="max"
            df = ticker_obj.history(period="max")

            if df.empty:
                print(f"No historical data found for {self.ticker}")
                return

            self.historical_data = df

            # Calculate Technical Indicators
            # SMA
            df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
            df['SMA_200'] = ta.trend.sma_indicator(df['Close'], window=200)

            # RSI
            df['RSI'] = ta.momentum.rsi(df['Close'], window=14)

            # Bollinger Bands (Volatility)
            bb = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
            df['BB_High'] = bb.bollinger_hband()
            df['BB_Low'] = bb.bollinger_lband()

            # Get latest values
            latest = df.iloc[-1]
            prev = df.iloc[-2]

            self.technicals = {
                'Current_Price': latest['Close'],
                'Change_1D': ((latest['Close'] - prev['Close']) / prev['Close']) * 100,
                'SMA_50': latest['SMA_50'],
                'SMA_200': latest['SMA_200'],
                'RSI': latest['RSI'],
                'Volatility_Band_Width': latest['BB_High'] - latest['BB_Low'],
                'Latest_Date': latest.name.strftime('%Y-%m-%d')
            }
            print(f"Successfully analyzed {len(df)} days of market data.")

        except Exception as e:
            print(f"Error analyzing market data: {e}")

    def generate_ai_prompt(self):
        print("Generating AI Analyst Briefing...")

        avg_sentiment = sum(self.sentiment_scores) / len(self.sentiment_scores) if self.sentiment_scores else 0

        prompt = f"""
ACT AS A SENIOR FINANCIAL ANALYST FOR A MAJOR HEDGE FUND.

YOUR TASK:
Analyze the provided data for ticker symbol {self.ticker} and provide a detailed market prediction.
You must account for technical indicators, historical price action, and current sentiment from news coverage.

### 1. TECHNICAL ANALYSIS (Based on Historical Data)
- Ticker: {self.ticker}
- Latest Date: {self.technicals.get('Latest_Date', 'N/A')}
- Current Price: ${self.technicals.get('Current_Price', 0):.2f}
- 1-Day Change: {self.technicals.get('Change_1D', 0):.2f}%
- RSI (14): {self.technicals.get('RSI', 0):.2f} (Over 70=Overbought, Under 30=Oversold)
- SMA 50: ${self.technicals.get('SMA_50', 0):.2f}
- SMA 200: ${self.technicals.get('SMA_200', 0):.2f}
- Market Condition: {"Bullish" if self.technicals.get('Current_Price', 0) > self.technicals.get('SMA_200', 0) else "Bearish"} (Price vs SMA 200)

### 2. SENTIMENT ANALYSIS (Based on Web Crawl)
- Source URL: {self.start_url}
- Articles Analyzed: {len(self.data)}
- Average Sentiment Score: {avg_sentiment:.2f} (-1.0 to 1.0)
- Corporate Profile: {self.corporate_profile[:500]}...

### 3. TOP HEADLINES
"""
        sorted_data = sorted(self.data, key=lambda x: abs(x['Sentiment']), reverse=True)[:10]
        for item in sorted_data:
            prompt += f"- {item['Headline']} (Sentiment: {item['Sentiment']:.2f})\n"

        prompt += """
### INSTRUCTIONS FOR THE BOT:
Based on the above, synthesize the technicals and sentiment.
1. Predict the likely price movement for the next week and next month.
2. Identify key resistance and support levels based on the SMA data.
3. Assess if the sentiment contradicts or supports the technical trend.
4. Provide a "BUY", "SELL", or "HOLD" recommendation with a confidence level (Low/Medium/High).

RESPONSE FORMAT:
Executive Summary:
Technical Outlook:
Sentiment Outlook:
Verdict & Prediction:
"""

        with open('ai_briefing.txt', 'w', encoding='utf-8') as f:
            f.write(prompt)
        print("AI Briefing saved to 'ai_briefing.txt'. Use this to prompt your AI bot.")
        return prompt

    def _sanitize_for_csv(self, value):
        """
        Sanitizes a value for CSV export to prevent Formula Injection.
        Prepends a single quote if the value starts with dangerous characters.
        """
        if isinstance(value, str) and value:
            # Dangerous characters that can trigger formula execution in spreadsheet software
            dangerous_chars = ('=', '+', '-', '@', '\t', '\r')
            if value[0] in dangerous_chars:
                return "'" + value
        return value

    def save_csv(self):
        if not self.data:
            print("No data to save to CSV.")
            return

        # Create a copy of the data to sanitize before saving
        sanitized_data = []
        for row in self.data:
            sanitized_row = {k: self._sanitize_for_csv(v) for k, v in row.items()}
            sanitized_data.append(sanitized_row)

        df = pd.DataFrame(sanitized_data)
        df.to_csv(self.csv_file, index=False)
        print(f"Data saved to {self.csv_file}")

    def generate_report(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=f"Market Report: {self.ticker}", ln=True, align='C')
        pdf.ln(10)

        # Disclaimer
        pdf.set_font("Arial", 'I', 10)
        pdf.set_text_color(255, 0, 0)
        disclaimer = "DISCLAIMER: This tool is for informational purposes only. Do not trade based on this."
        pdf.multi_cell(0, 5, txt=disclaimer)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(10)

        # Technical Summary
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="Technical Analysis", ln=True)
        pdf.set_font("Arial", size=11)

        if self.technicals:
            pdf.cell(200, 8, txt=f"Price: ${self.technicals.get('Current_Price', 0):.2f}", ln=True)
            pdf.cell(200, 8, txt=f"RSI: {self.technicals.get('RSI', 0):.2f}", ln=True)
            pdf.cell(200, 8, txt=f"SMA 50: ${self.technicals.get('SMA_50', 0):.2f}", ln=True)
            pdf.cell(200, 8, txt=f"SMA 200: ${self.technicals.get('SMA_200', 0):.2f}", ln=True)
        else:
            pdf.cell(200, 8, txt="No historical data available.", ln=True)
        pdf.ln(5)

        # Sentiment Summary
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="Sentiment Analysis", ln=True)
        pdf.set_font("Arial", size=11)

        avg_sentiment = sum(self.sentiment_scores) / len(self.sentiment_scores) if self.sentiment_scores else 0
        pdf.cell(200, 8, txt=f"Headlines Scanned: {len(self.data)}", ln=True)
        pdf.cell(200, 8, txt=f"Avg Sentiment: {avg_sentiment:.2f}", ln=True)

        outlook = "NEUTRAL"
        if avg_sentiment > 0.1:
            outlook = "BULLISH"
        elif avg_sentiment < -0.1:
            outlook = "BEARISH"
        pdf.cell(200, 8, txt=f"Sentiment Outlook: {outlook}", ln=True)
        pdf.ln(10)

        # AI Prompt Note
        pdf.set_font("Arial", 'I', 10)
        pdf.multi_cell(0, 5, txt="Detailed AI analysis prompt has been generated in 'ai_briefing.txt'.")

        pdf.output(self.pdf_file)
        print(f"Report saved to {self.pdf_file}")

    def run(self):
        print(f"Starting Financial Spyder for {self.ticker}...")

        # Step 1: Get Historical Data
        self.get_historical_data()

        # Step 2: Crawl for News
        self.crawl()

        # Step 3: Analyze & Save
        self.save_csv()
        self.generate_report()
        self.generate_ai_prompt()
        print("Done.")

if __name__ == "__main__":
    # Example usage
    # You can change the URL to a financial news site or company page
    spider = FinancialSpyder(
        start_url='https://finance.yahoo.com',
        ticker='SPY',
        csv_file='financial_data.csv',
        pdf_file='market_report.pdf',
        max_depth=2,
        max_pages=5
    )
    spider.run()
