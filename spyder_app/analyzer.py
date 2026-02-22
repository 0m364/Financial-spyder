import pandas as pd
import yfinance as yf
import ta
from textblob import TextBlob
import datetime

class SentimentAnalyzer:
    def analyze(self, text):
        blob = TextBlob(text)
        return blob.sentiment.polarity

class TechnicalAnalyzer:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = None
        self.technicals = {}

    def fetch_history(self, period="max"):
        print(f"Fetching historical data for {self.ticker}...")
        try:
            ticker_obj = yf.Ticker(self.ticker)
            self.data = ticker_obj.history(period=period)
            if self.data.empty:
                print(f"No historical data found for {self.ticker}")
                return False
            return True
        except Exception as e:
            print(f"Error fetching data: {e}")
            return False

    def calculate_indicators(self):
        if self.data is None or self.data.empty:
            return

        df = self.data

        # Basic Indicators
        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['SMA_200'] = ta.trend.sma_indicator(df['Close'], window=200)
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)

        bb = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
        df['BB_High'] = bb.bollinger_hband()
        df['BB_Low'] = bb.bollinger_lband()

        # Update technicals dict with latest values
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

    def calculate_premium_indicators(self):
        if self.data is None or self.data.empty:
            return

        df = self.data

        # MACD
        df['MACD'] = ta.trend.macd(df['Close'])
        df['MACD_Signal'] = ta.trend.macd_signal(df['Close'])

        # Stochastic
        df['Stoch_K'] = ta.momentum.stoch(df['High'], df['Low'], df['Close'])
        df['Stoch_D'] = ta.momentum.stoch_signal(df['High'], df['Low'], df['Close'])

        # ATR
        df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'])

        latest = df.iloc[-1]
        self.technicals.update({
            'MACD': latest['MACD'],
            'MACD_Signal': latest['MACD_Signal'],
            'Stoch_K': latest['Stoch_K'],
            'Stoch_D': latest['Stoch_D'],
            'ATR': latest['ATR']
        })

    def get_market_condition(self):
        if not self.technicals:
            return "Unknown"
        price = self.technicals.get('Current_Price', 0)
        sma200 = self.technicals.get('SMA_200', 0)
        if price > sma200:
            return "Bullish"
        return "Bearish"
