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
import socket

class TestSSRFCrawler(unittest.TestCase):

    @patch('socket.getaddrinfo')
    def test_is_safe_url_public(self, mock_getaddrinfo):
        mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('8.8.8.8', 0))]
        self.assertTrue(is_safe_url('http://example.com'))
        self.assertTrue(is_safe_url('https://example.com'))

    @patch('socket.getaddrinfo')
    def test_is_safe_url_private(self, mock_getaddrinfo):
        # Localhost
        mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('127.0.0.1', 0))]
        self.assertFalse(is_safe_url('http://localhost'))

        # Private IP space
        mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('10.0.0.1', 0))]
        self.assertFalse(is_safe_url('http://10.0.0.1'))

        mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('192.168.1.100', 0))]
        self.assertFalse(is_safe_url('http://192.168.1.100'))

        # Link-local
        mock_getaddrinfo.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('169.254.169.254', 0))]
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
