import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import pandas as pd
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Corporate_SPYder import FinancialSpyder

class TestFinancialSpyderAnalysis(unittest.TestCase):
    def setUp(self):
        self.csv_file = 'test_data_analysis.csv'
        self.pdf_file = 'test_report_analysis.pdf'
        self.spider = FinancialSpyder(
            start_url='http://test.com',
            ticker='TEST',
            csv_file=self.csv_file,
            pdf_file=self.pdf_file
        )
        self.spider.data = []

    def tearDown(self):
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)
        if os.path.exists(self.pdf_file):
            os.remove(self.pdf_file)
        if os.path.exists('ai_briefing.txt'):
            os.remove('ai_briefing.txt')

    @patch('yfinance.Ticker')
    def test_get_historical_data(self, mock_ticker):
        # Create a mock DataFrame with enough data points for indicators (at least 200 for SMA_200)
        dates = pd.date_range(start='2020-01-01', periods=250)
        data = {
            'Open': np.random.rand(250) * 100,
            'High': np.random.rand(250) * 100,
            'Low': np.random.rand(250) * 100,
            'Close': np.linspace(100, 200, 250), # Upward trend
            'Volume': np.random.randint(1000, 10000, 250)
        }
        df = pd.DataFrame(data, index=dates)

        # Configure mock
        mock_instance = MagicMock()
        mock_instance.history.return_value = df
        mock_ticker.return_value = mock_instance

        self.spider.get_historical_data()

        # Check if technicals were calculated
        self.assertIsNotNone(self.spider.technicals)
        self.assertIn('Current_Price', self.spider.technicals)
        self.assertIn('SMA_50', self.spider.technicals)
        self.assertIn('SMA_200', self.spider.technicals)
        self.assertIn('RSI', self.spider.technicals)

        # Verify basic calculation logic (last price should match mock data)
        self.assertAlmostEqual(self.spider.technicals['Current_Price'], 200.0)

    def test_generate_ai_prompt(self):
        # Setup mock data
        self.spider.technicals = {
            'Current_Price': 150.0,
            'Change_1D': 1.5,
            'RSI': 65,
            'SMA_50': 145,
            'SMA_200': 140,
            'Latest_Date': '2023-01-01'
        }
        self.spider.data = [
            {'Headline': 'Good Earnings', 'Sentiment': 0.8, 'URL': 'http://test.com'}
        ]
        self.spider.sentiment_scores = [0.8]
        self.spider.corporate_profile = "A great company."

        prompt = self.spider.generate_ai_prompt()

        self.assertIn("ACT AS A SENIOR FINANCIAL ANALYST", prompt)
        self.assertIn("Good Earnings", prompt)
        self.assertIn("Current Price: $150.00", prompt)
        self.assertTrue(os.path.exists('ai_briefing.txt'))

if __name__ == '__main__':
    unittest.main()
