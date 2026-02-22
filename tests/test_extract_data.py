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

import unittest

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spyder_app.crawler import WebCrawler

class TestExtractData(unittest.TestCase):
    def setUp(self):
        self.crawler = WebCrawler(start_url='http://test.com')
        # Mock sentiment analyzer
        self.crawler.sentiment_analyzer = MagicMock()
        self.crawler.sentiment_analyzer.analyze.return_value = 0.5

    def test_extract_headlines(self):
        mock_soup = MagicMock()

        h1 = MagicMock()
        h1.get_text.return_value = "Headline 1"
        h2 = MagicMock()
        h2.get_text.return_value = "Headline 2"
        h3 = MagicMock()
        h3.get_text.return_value = "Headline 3"

        mock_soup.find_all.return_value = [h1, h2, h3]

        # Configure find_all to return headlines when called with ['h1', 'h2', 'h3']
        # But wait, find_all is also called for 'a' tags later in extract_data?
        # No, extract_data calls find_all(['h1', 'h2', 'h3']).
        # Crawl calls find_all('a').
        # We are testing extract_data only.

        self.crawler.extract_data(mock_soup, "http://test.com")

        mock_soup.find_all.assert_called_with(['h1', 'h2', 'h3'])
        self.assertEqual(len(self.crawler.data), 3)
        self.assertEqual(self.crawler.data[0]['Headline'], "Headline 1")

    def test_corporate_profile_selection(self):
        mock_soup = MagicMock()

        # We need to simulate the candidates finding
        # The code does:
        # profile_candidates = [soup.find(...), soup.find(...), ...]

        # Let's say the first one matches
        candidate1 = MagicMock()
        candidate1.get_text.return_value = "Profile Content"

        # side_effect for soup.find to return candidate1 for the first call
        mock_soup.find.side_effect = [candidate1, None, None, None]

        self.crawler.extract_data(mock_soup, "http://test.com")
        self.assertEqual(self.crawler.corporate_profile, "Profile Content")

    def test_corporate_profile_no_overwrite(self):
        self.crawler.corporate_profile = "Original Profile"
        mock_soup = MagicMock()

        self.crawler.extract_data(mock_soup, "http://test.com")
        self.assertEqual(self.crawler.corporate_profile, "Original Profile")

if __name__ == '__main__':
    unittest.main()
