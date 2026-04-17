import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock dependencies before importing spyder_app
sys.modules["yfinance"] = MagicMock()
sys.modules["ta"] = MagicMock()
sys.modules["textblob"] = MagicMock()
sys.modules["fpdf"] = MagicMock()
sys.modules["playwright"] = MagicMock()
sys.modules["playwright.sync_api"] = MagicMock()
sys.modules["pandas"] = MagicMock()
sys.modules["requests"] = MagicMock()
sys.modules["bs4"] = MagicMock()

from spyder_app.core import PremiumSpyder

class TestExperimentalLogic(unittest.TestCase):
    def setUp(self):
        self.ticker = "TEST"
        self.start_url = "http://test.com"
        self.csv_file = "test.csv"
        self.pdf_file = "test.pdf"
        self.spyder = PremiumSpyder(self.start_url, self.ticker, self.csv_file, self.pdf_file)
        self.spyder.analyzer = MagicMock()
        self.spyder.analyzer.technicals = {"Current_Price": 100}

    def _create_mock_df(self, prices):
        df = MagicMock()
        df.empty = False
        df.__len__.return_value = len(prices)

        class IlocIndexer:
            def __getitem__(self, idx):
                real_idx = len(prices) + idx
                mock_row = MagicMock()
                def getitem_side_effect(key):
                    if key == "Close":
                        return prices[real_idx]
                    return None
                mock_row.__getitem__.side_effect = getitem_side_effect
                return mock_row

        df.iloc = IlocIndexer()
        return df

    def test_apply_fibonacci_scaling_no_losses(self):
        df = self._create_mock_df([100, 105, 110])
        initial_score = 50
        new_score = self.spyder._apply_fibonacci_scaling(df, initial_score)
        self.assertEqual(new_score, initial_score)
        self.assertEqual(self.spyder.analyzer.technicals["Fibonacci_Multiplier"], 0)

    def test_apply_fibonacci_scaling_one_loss(self):
        df = self._create_mock_df([100, 110, 105])
        initial_score = 50
        new_score = self.spyder._apply_fibonacci_scaling(df, initial_score)
        self.assertEqual(new_score, 52)
        self.assertEqual(self.spyder.analyzer.technicals["Fibonacci_Multiplier"], 1)

    def test_apply_fibonacci_scaling_three_losses(self):
        df = self._create_mock_df([120, 115, 110, 105])
        initial_score = 50
        new_score = self.spyder._apply_fibonacci_scaling(df, initial_score)
        self.assertEqual(new_score, 56)
        self.assertEqual(self.spyder.analyzer.technicals["Fibonacci_Multiplier"], 3)

    def test_apply_fibonacci_scaling_max_losses(self):
        df = self._create_mock_df([140, 135, 130, 125, 120, 115, 110, 105])
        initial_score = 50
        new_score = self.spyder._apply_fibonacci_scaling(df, initial_score)
        self.assertEqual(new_score, 50)
        self.assertEqual(self.spyder.analyzer.technicals["Fibonacci_Multiplier"], 0)

    def test_apply_fibonacci_scaling_zero_price(self):
        self.spyder.analyzer.technicals["Current_Price"] = 0
        df = self._create_mock_df([100, 110, 105])
        initial_score = 50
        new_score = self.spyder._apply_fibonacci_scaling(df, initial_score)
        self.assertEqual(new_score, 50)
        self.assertNotIn("Fibonacci_Multiplier", self.spyder.analyzer.technicals)

    def test_apply_martingale_proxy_loss(self):
        df = self._create_mock_df([110, 105])
        initial_score = 50
        new_score = self.spyder._apply_martingale_proxy(df, initial_score)
        self.assertEqual(new_score, 60)
        self.assertTrue(self.spyder.analyzer.technicals["Martingale_Active"])

    def test_apply_martingale_proxy_win(self):
        df = self._create_mock_df([105, 110])
        initial_score = 50
        new_score = self.spyder._apply_martingale_proxy(df, initial_score)
        self.assertEqual(new_score, 50)
        self.assertFalse(self.spyder.analyzer.technicals["Martingale_Active"])

    def test_apply_gamblers_fallacy_triggered(self):
        df = self._create_mock_df([120, 115, 110, 105])
        initial_score = 50
        new_score = self.spyder._apply_gamblers_fallacy(df, initial_score)
        self.assertEqual(new_score, 70)
        self.assertTrue(self.spyder.analyzer.technicals["Gamblers_Fallacy_Triggered"])

    def test_apply_gamblers_fallacy_not_triggered(self):
        df = self._create_mock_df([100, 105, 110, 115])
        initial_score = 50
        new_score = self.spyder._apply_gamblers_fallacy(df, initial_score)
        self.assertEqual(new_score, 50)
        self.assertFalse(self.spyder.analyzer.technicals["Gamblers_Fallacy_Triggered"])

    def test_apply_kelly_criterion(self):
        prices = [100 + i for i in range(30)]
        df = self._create_mock_df(prices)
        initial_score = 50
        with patch.object(df, 'tail') as mock_tail:
            mock_close = MagicMock()
            mock_tail.return_value = {"Close": mock_close}
            mock_diff = mock_close.diff.return_value
            mock_gt = MagicMock()
            mock_diff.__gt__.return_value = mock_gt
            mock_gt.sum.return_value = 21 # 70% win rate

            new_score = self.spyder._apply_kelly_criterion(df, initial_score)
            self.assertEqual(new_score, 58)

if __name__ == "__main__":
    unittest.main()
