import pandas as pd
from fpdf import FPDF
import os

class Reporter:
    def __init__(self, ticker, data, technicals, sentiment_scores, corporate_profile):
        self.ticker = ticker
        self.data = data
        self.technicals = technicals
        self.sentiment_scores = sentiment_scores
        self.corporate_profile = corporate_profile
        self.avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

    def save_csv(self, filename):
        if not self.data:
            print("No data to save to CSV.")
            return

        filename = os.path.basename(filename)
        sanitized_data = []
        for row in self.data:
            sanitized_row = {k: self._sanitize_for_csv(v) for k, v in row.items()}
            sanitized_data.append(sanitized_row)

        df = pd.DataFrame(sanitized_data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

    def _sanitize_for_csv(self, value):
        if isinstance(value, str) and value:
            dangerous_chars = ('=', '+', '-', '@', '\t', '\r')
            if value[0] in dangerous_chars:
                return "'" + value
        return value

    def generate_pdf(self, filename, tier='Free'):
        filename = os.path.basename(filename)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=f"Market Report ({tier} Version): {self.ticker}", ln=True, align='C')
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

            if tier == 'Premium':
                pdf.cell(200, 8, txt=f"MACD: {self.technicals.get('MACD', 0):.4f}", ln=True)
                pdf.cell(200, 8, txt=f"Stochastic K: {self.technicals.get('Stoch_K', 0):.2f}", ln=True)
                pdf.cell(200, 8, txt=f"ATR: {self.technicals.get('ATR', 0):.4f}", ln=True)

                # Prediction Score
                score = self.technicals.get('Prediction_Score', 0)
                pdf.set_font("Arial", 'B', 12)
                pdf.set_text_color(0, 128, 0)
                pdf.cell(200, 8, txt=f"AI Prediction Score: {score:.1f}/100", ln=True)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Arial", size=11)
        else:
            pdf.cell(200, 8, txt="No historical data available.", ln=True)
        pdf.ln(5)

        # Sentiment Summary
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="Sentiment Analysis", ln=True)
        pdf.set_font("Arial", size=11)

        pdf.cell(200, 8, txt=f"Headlines Scanned: {len(self.data)}", ln=True)
        pdf.cell(200, 8, txt=f"Avg Sentiment: {self.avg_sentiment:.2f}", ln=True)

        outlook = "NEUTRAL"
        if self.avg_sentiment > 0.1:
            outlook = "BULLISH"
        elif self.avg_sentiment < -0.1:
            outlook = "BEARISH"
        pdf.cell(200, 8, txt=f"Sentiment Outlook: {outlook}", ln=True)
        pdf.ln(10)

        # Weather Forecast (Premium)
        if tier == 'Premium':
            self._add_weather_forecast(pdf)

        pdf.output(filename)
        print(f"Report saved to {filename}")

    def _add_weather_forecast(self, pdf):
        score = self.technicals.get('Prediction_Score', 50)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="Market Weather Forecast", ln=True)
        pdf.set_font("Arial", size=11)

        score = self.technicals.get('Prediction_Score', 50)

        # Condition
        condition = "Cloudy"
        if score > 70: condition = "Sunny (Bullish)"
        elif score > 60: condition = "Partly Cloudy (Slightly Bullish)"
        elif score < 30: condition = "Stormy (Bearish)"
        elif score < 40: condition = "Rainy (Slightly Bearish)"

        pdf.cell(200, 8, txt=f"Condition: {condition}", ln=True)
        pdf.cell(200, 8, txt=f"Bull Probability: {score:.1f}%", ln=True)
        pdf.cell(200, 8, txt=f"Bear Probability: {100-score:.1f}%", ln=True)

        # Factors
        geo = self.technicals.get('Geopolitical_Score', 0)
        env = self.technicals.get('Environmental_Score', 0)

        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 8, txt="Factor Analysis", ln=True)
        pdf.set_font("Arial", size=11)

        geo_text = "Neutral"
        if geo > 0.1: geo_text = "Positive"
        elif geo < -0.1: geo_text = "Negative (Risk)"
        pdf.cell(200, 8, txt=f"Geopolitical Factor: {geo_text}", ln=True)

        env_text = "Neutral"
        if env > 0.1: env_text = "Positive"
        elif env < -0.1: env_text = "Negative (Risk)"
        pdf.cell(200, 8, txt=f"Environmental Factor: {env_text}", ln=True)

    def generate_ai_prompt(self, filename, start_url):
        print("Generating AI Analyst Briefing...")
        filename = os.path.basename(filename)

        prompt = f"""
ACT AS A SENIOR FINANCIAL ANALYST FOR A MAJOR HEDGE FUND.

YOUR TASK:
Analyze the provided data for ticker symbol {self.ticker} and provide a detailed market prediction.

### 1. TECHNICAL ANALYSIS (Based on Historical Data)
- Current Price: ${self.technicals.get('Current_Price', 0):.2f}
- RSI (14): {self.technicals.get('RSI', 0):.2f}
- SMA 50: ${self.technicals.get('SMA_50', 0):.2f}
- SMA 200: ${self.technicals.get('SMA_200', 0):.2f}
"""
        if 'MACD' in self.technicals:
             prompt += f"- MACD: {self.technicals.get('MACD', 0):.4f}\n"
             prompt += f"- Automated Prediction Score: {self.technicals.get('Prediction_Score', 0):.1f}/100\n"
             prompt += f"- Geopolitical Factor Score: {self.technicals.get('Geopolitical_Score', 0):.2f}\n"
             prompt += f"- Environmental Factor Score: {self.technicals.get('Environmental_Score', 0):.2f}\n"

        prompt += f"""
### 2. SENTIMENT ANALYSIS (Based on Web Crawl)
- Source URL: {start_url}
- Average Sentiment Score: {self.avg_sentiment:.2f}
- Corporate Profile: {self.corporate_profile[:500]}...

### 3. TOP HEADLINES
"""
        sorted_data = sorted(self.data, key=lambda x: abs(x['Sentiment']), reverse=True)[:10]
        for item in sorted_data:
            prompt += f"- {item['Headline']} (Sentiment: {item['Sentiment']:.2f})\n"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(prompt)
        print(f"AI Briefing saved to '{filename}'.")
