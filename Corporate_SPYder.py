import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from fpdf import FPDF

def crawl_web(url, csv_file, pdf_file):
    visited = set()
    queue = [url]
    news_data = []

    while queue:
        current_url = queue.pop(0)
        if current_url in visited:
            continue

        try:
            response = requests.get(current_url)
        except requests.exceptions.RequestException:
            continue

        visited.add(current_url)

        soup = BeautifulSoup(response.content, 'html.parser')

        # You'll need to inspect the website to see what tag or class the data you want is in.
        headlines = soup.find_all('h1')
        for headline in headlines:
            news_data.append(headline.text)

        # Save data to CSV
        df = pd.DataFrame(news_data, columns=['Headline'])
        df.to_csv(csv_file, index=False)

        # Extract corporate profile data
        corp_profile = soup.find('div', {'class': 'corporate-profile'})
        if corp_profile:
            # Create a PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size = 15)

            # Add text to PDF
            pdf.cell(200, 10, txt = corp_profile.text, ln = True, align = 'C')

            # Save the pdf with name .pdf
            pdf.output(pdf_file)

        for link in soup.find_all('a'):
            next_url = link.get('href')
            if next_url and next_url.startswith('http'):
                queue.append(next_url)

# Usage example:
crawl_web('https://www.example.com', 'news.csv', 'corporate_profile.pdf')
