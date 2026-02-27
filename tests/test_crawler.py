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

from spyder_app.crawler import WebCrawler

class TestCrawlerSafeURL(unittest.TestCase):
    def setUp(self):
        self.crawler = WebCrawler('http://example.com')

    @patch('spyder_app.crawler.socket.gethostbyname')
    def test_is_safe_url_public_ip(self, mock_gethostbyname):
        mock_gethostbyname.return_value = '93.184.216.34' # example.com IP
        self.assertTrue(self.crawler.is_safe_url('http://example.com'))
        self.assertTrue(self.crawler.is_safe_url('https://example.com'))

    @patch('spyder_app.crawler.socket.gethostbyname')
    def test_is_safe_url_private_ip(self, mock_gethostbyname):
        # Localhost
        mock_gethostbyname.return_value = '127.0.0.1'
        self.assertFalse(self.crawler.is_safe_url('http://localhost'))
        self.assertFalse(self.crawler.is_safe_url('http://127.0.0.1'))

        # Private IP 10.x.x.x
        mock_gethostbyname.return_value = '10.0.0.1'
        self.assertFalse(self.crawler.is_safe_url('http://internal.service.local'))

        # Link-local / Cloud metadata IP
        mock_gethostbyname.return_value = '169.254.169.254'
        self.assertFalse(self.crawler.is_safe_url('http://169.254.169.254/latest/meta-data/'))

    def test_is_safe_url_invalid_scheme(self):
        self.assertFalse(self.crawler.is_safe_url('ftp://example.com'))
        self.assertFalse(self.crawler.is_safe_url('file:///etc/passwd'))

    @patch('spyder_app.crawler.socket.gethostbyname')
    def test_is_safe_url_unresolvable(self, mock_gethostbyname):
        import socket
        mock_gethostbyname.side_effect = socket.gaierror
        self.assertFalse(self.crawler.is_safe_url('http://thisdomaindoesnotexist.com'))

if __name__ == '__main__':
    unittest.main()
