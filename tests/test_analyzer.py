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
        self.analyzer = TechnicalAnalyzer('TEST')

    @patch('spyder_app.analyzer.yf.Ticker')
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
        mock_ticker_class.assert_called_with('TEST')
        mock_ticker_obj.history.assert_called_with(period="1y")

if __name__ == '__main__':
    unittest.main()
