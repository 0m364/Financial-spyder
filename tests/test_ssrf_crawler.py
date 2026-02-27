import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock dependencies before importing spyder_app
sys.modules['pandas'] = MagicMock()
sys.modules['yfinance'] = MagicMock()
sys.modules['ta'] = MagicMock()
sys.modules['textblob'] = MagicMock()
sys.modules['fpdf'] = MagicMock()
sys.modules['playwright'] = MagicMock()
sys.modules['playwright.sync_api'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['bs4'] = MagicMock()

from spyder_app.crawler import is_safe_url, WebCrawler

class TestSSRFCrawler(unittest.TestCase):

    @patch('socket.gethostbyname')
    def test_is_safe_url_public(self, mock_gethostbyname):
        mock_gethostbyname.return_value = '8.8.8.8'
        self.assertTrue(is_safe_url('http://example.com'))
        self.assertTrue(is_safe_url('https://example.com'))

    @patch('socket.gethostbyname')
    def test_is_safe_url_private(self, mock_gethostbyname):
        # Localhost
        mock_gethostbyname.return_value = '127.0.0.1'
        self.assertFalse(is_safe_url('http://localhost'))

        # Private IP space
        mock_gethostbyname.return_value = '10.0.0.1'
        self.assertFalse(is_safe_url('http://10.0.0.1'))

        mock_gethostbyname.return_value = '192.168.1.100'
        self.assertFalse(is_safe_url('http://192.168.1.100'))

        # Link-local
        mock_gethostbyname.return_value = '169.254.169.254'
        self.assertFalse(is_safe_url('http://169.254.169.254'))

    def test_is_safe_url_invalid_schemes(self):
        self.assertFalse(is_safe_url('file:///etc/passwd'))
        self.assertFalse(is_safe_url('ftp://example.com'))
        self.assertFalse(is_safe_url('gopher://example.com'))
        self.assertFalse(is_safe_url('dict://example.com'))

    @patch('spyder_app.crawler.requests.get')
    def test_crawler_skips_unsafe_urls(self, mock_requests_get):

        # Start url that points to a link-local ip (aws metadata service)
        crawler = WebCrawler('http://169.254.169.254/latest/meta-data/')
        crawler.crawl()

        # Ensure no requests were made
        mock_requests_get.assert_not_called()

if __name__ == '__main__':
    unittest.main()
