import sys
from unittest.mock import MagicMock, patch
import os

# Mock dependencies
sys.modules["requests"] = MagicMock()
sys.modules["pandas"] = MagicMock()
sys.modules["fpdf"] = MagicMock()
sys.modules["textblob"] = MagicMock()
sys.modules["yfinance"] = MagicMock()
sys.modules["ta"] = MagicMock()
sys.modules["bs4"] = MagicMock()
sys.modules["playwright"] = MagicMock()
sys.modules["playwright.sync_api"] = MagicMock()

import unittest

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spyder_app.analyzer import TechnicalAnalyzer


class TestTechnicalAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = TechnicalAnalyzer("TEST")

    @patch("spyder_app.analyzer.yf.Ticker")
    def test_fetch_history_empty_data(self, mock_ticker_class):
        # Create a mock for the ticker object returned by yf.Ticker
        mock_ticker_obj = MagicMock()

        # Configure the mock to return an empty DataFrame-like object for history()
        # Since pandas is mocked, we need an object that has an 'empty' attribute set to True
        mock_empty_df = MagicMock()
        mock_empty_df.empty = True

        mock_ticker_obj.history.return_value = mock_empty_df

        # Make yf.Ticker('TEST') return our configured mock
        mock_ticker_class.return_value = mock_ticker_obj

        # Call fetch_history
        result = self.analyzer.fetch_history(period="1y")

        # Verify the result and that it checks the empty condition properly
        self.assertFalse(result)
        mock_ticker_class.assert_called_with("TEST")
        mock_ticker_obj.history.assert_called_with(period="1y")


if __name__ == "__main__":
    unittest.main()

    @patch('spyder_app.analyzer.yf.Ticker')
    def test_calculate_indicators(self, mock_ticker_class):
        # Setup mock pandas DataFrame with 50 rows of dummy data to satisfy SMA_50
        mock_df = MagicMock()

        import datetime

        # We need realistic DataFrame structure to pass ta functions
        import pandas as pd
        import numpy as np

        # Create a simple DataFrame for testing
        dates = pd.date_range(start='1/1/2020', periods=200)
        df = pd.DataFrame(index=dates)
        df['Close'] = [100.0] * 200
        df['High'] = [105.0] * 200
        df['Low'] = [95.0] * 200

        self.analyzer.data = df

        # Ensure 'ta' module doesn't error when calculating
        with patch('spyder_app.analyzer.ta') as mock_ta:
            # Mock ta functions
            mock_ta.trend.sma_indicator.return_value = pd.Series([100.0] * 200, index=dates)
            mock_ta.momentum.rsi.return_value = pd.Series([50.0] * 200, index=dates)

            mock_bb = MagicMock()
            mock_bb.bollinger_hband.return_value = pd.Series([105.0] * 200, index=dates)
            mock_bb.bollinger_lband.return_value = pd.Series([95.0] * 200, index=dates)
            mock_ta.volatility.BollingerBands.return_value = mock_bb

            self.analyzer.calculate_indicators()

            # Verify technicals are populated
            self.assertEqual(self.analyzer.technicals['Current_Price'], 100.0)
            self.assertEqual(self.analyzer.technicals['SMA_50'], 100.0)
            self.assertEqual(self.analyzer.technicals['RSI'], 50.0)
            self.assertEqual(self.analyzer.technicals['Volatility_Band_Width'], 10.0)
