import sys
from unittest.mock import MagicMock, patch
import os

# Mock dependencies
sys.modules["requests"] = MagicMock()
sys.modules["pandas"] = MagicMock()
sys.modules["numpy"] = MagicMock()
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

    def test_calculate_indicators(self):
        # Setup mock DataFrame
        mock_df = MagicMock()
        mock_df.empty = False

        # Mock rows for iloc
        mock_latest = MagicMock()
        # Mocking __getitem__ for the row object
        mock_latest.__getitem__.side_effect = lambda key: {
            "Close": 100.0,
            "SMA_50": 100.0,
            "SMA_200": 100.0,
            "RSI": 50.0,
            "BB_High": 105.0,
            "BB_Low": 95.0
        }[key]
        mock_latest.name.strftime.return_value = "2020-01-01"

        mock_prev = MagicMock()
        mock_prev.__getitem__.side_effect = lambda key: 90.0 if key == "Close" else None

        # Use side_effect for iloc
        mock_df.iloc.__getitem__.side_effect = lambda idx: mock_latest if idx == -1 else mock_prev

        self.analyzer.data = mock_df

        with patch('spyder_app.analyzer.ta') as mock_ta:
            # Mock ta functions
            mock_ta.trend.sma_indicator.return_value = "SMA_50_SERIES"
            mock_ta.momentum.rsi.return_value = "RSI_SERIES"

            mock_bb = MagicMock()
            mock_bb.bollinger_hband.return_value = "BB_HIGH_SERIES"
            mock_bb.bollinger_lband.return_value = "BB_LOW_SERIES"
            mock_ta.volatility.BollingerBands.return_value = mock_bb

            self.analyzer.calculate_indicators()

            # Verify technicals are populated correctly
            self.assertEqual(self.analyzer.technicals['Current_Price'], 100.0)
            self.assertEqual(self.analyzer.technicals['SMA_50'], 100.0)
            self.assertEqual(self.analyzer.technicals['RSI'], 50.0)
            self.assertEqual(self.analyzer.technicals['Volatility_Band_Width'], 10.0)
            self.assertEqual(self.analyzer.technicals['Latest_Date'], "2020-01-01")

    def test_calculate_premium_indicators(self):
        # Setup mock DataFrame
        mock_df = MagicMock()
        mock_df.empty = False

        mock_latest = MagicMock()
        mock_latest.__getitem__.side_effect = lambda key: {
            "MACD": 1.5,
            "MACD_Signal": 1.0,
            "Stoch_K": 80.0,
            "Stoch_D": 75.0,
            "ATR": 2.0
        }[key]

        mock_df.iloc.__getitem__.return_value = mock_latest
        self.analyzer.data = mock_df

        # Pre-populate technicals to check update behavior
        self.analyzer.technicals = {"Existing": "Data"}

        with patch('spyder_app.analyzer.ta') as mock_ta:
            self.analyzer.calculate_premium_indicators()

            # Verify ta functions were called
            mock_ta.trend.macd.assert_called()
            mock_ta.trend.macd_signal.assert_called()
            mock_ta.momentum.stoch.assert_called()
            mock_ta.momentum.stoch_signal.assert_called()
            mock_ta.volatility.average_true_range.assert_called()

            # Verify technicals were updated
            self.assertEqual(self.analyzer.technicals["MACD"], 1.5)
            self.assertEqual(self.analyzer.technicals["ATR"], 2.0)
            self.assertEqual(self.analyzer.technicals["Existing"], "Data")

    def test_calculate_premium_indicators_no_data(self):
        # Test with None
        self.analyzer.data = None
        self.analyzer.calculate_premium_indicators()
        self.assertEqual(self.analyzer.technicals, {})

        # Test with empty DataFrame
        mock_df = MagicMock()
        mock_df.empty = True
        self.analyzer.data = mock_df
        self.analyzer.calculate_premium_indicators()
        self.assertEqual(self.analyzer.technicals, {})


if __name__ == "__main__":
    unittest.main()
