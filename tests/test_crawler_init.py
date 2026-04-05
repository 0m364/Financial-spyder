import unittest
from unittest.mock import MagicMock
import sys
import os
from urllib.parse import urlparse

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock dependencies before importing spyder_app
sys.modules["textblob"] = MagicMock()
sys.modules["requests"] = MagicMock()
sys.modules["bs4"] = MagicMock()
sys.modules["yfinance"] = MagicMock()
sys.modules["ta"] = MagicMock()
sys.modules["pandas"] = MagicMock()
sys.modules["fpdf"] = MagicMock()
sys.modules["playwright"] = MagicMock()
sys.modules["playwright.sync_api"] = MagicMock()

from spyder_app.crawler import WebCrawler

class TestWebCrawlerInit(unittest.TestCase):
    def test_default_initialization(self):
        url = "http://example.com"
        crawler = WebCrawler(url)
        self.assertEqual(crawler.start_url, url)
        self.assertEqual(crawler.start_url_parsed, urlparse(url))
        self.assertEqual(crawler.max_depth, 2)
        self.assertEqual(crawler.max_pages, 10)
        self.assertEqual(crawler.visited, set())
        self.assertEqual(crawler.page_count, 0)
        self.assertEqual(crawler.data, [])
        self.assertEqual(crawler.corporate_profile, "")
        self.assertEqual(crawler.sentiment_scores, [])
        self.assertIsNotNone(crawler.sentiment_analyzer)
        self.assertEqual(crawler.factors, {
            "Geopolitical": 0,
            "Environmental": 0,
            "Count_Geo": 0,
            "Count_Env": 0,
        })

    def test_custom_initialization(self):
        url = "https://test.org"
        crawler = WebCrawler(url, max_depth=5, max_pages=100)
        self.assertEqual(crawler.start_url, url)
        self.assertEqual(crawler.max_depth, 5)
        self.assertEqual(crawler.max_pages, 100)

if __name__ == "__main__":
    unittest.main()
