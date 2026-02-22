import sys
from unittest.mock import MagicMock, patch

# Mock dependencies before importing FinancialSpyder
# This is necessary because the current environment lacks these dependencies
# and has no internet access to install them.
sys.modules["requests"] = MagicMock()
sys.modules["pandas"] = MagicMock()
sys.modules["fpdf"] = MagicMock()
sys.modules["textblob"] = MagicMock()
sys.modules["yfinance"] = MagicMock()
sys.modules["ta"] = MagicMock()
sys.modules["bs4"] = MagicMock()

import unittest
import os

# Add parent directory to path to import Corporate_SPYder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Corporate_SPYder import FinancialSpyder

class TestExtractData(unittest.TestCase):
    def setUp(self):
        self.spider = FinancialSpyder(
            start_url='http://test.com',
            ticker='TEST',
            csv_file='test.csv',
            pdf_file='test.pdf'
        )
        # Mock analyze_sentiment to return a fixed value
        self.spider.analyze_sentiment = MagicMock(return_value=0.5)

    def test_extract_headlines(self):
        """Test extraction of h1, h2, h3 headlines."""
        mock_soup = MagicMock()

        h1 = MagicMock()
        h1.get_text.return_value = "Headline 1"
        h2 = MagicMock()
        h2.get_text.return_value = "Headline 2"
        h3 = MagicMock()
        h3.get_text.return_value = "Headline 3"

        mock_soup.find_all.return_value = [h1, h2, h3]

        self.spider.extract_data(mock_soup, "http://test.com")

        mock_soup.find_all.assert_called_with(['h1', 'h2', 'h3'])
        self.assertEqual(len(self.spider.data), 3)
        self.assertEqual(self.spider.data[0]['Headline'], "Headline 1")
        self.assertEqual(self.spider.data[1]['Headline'], "Headline 2")
        self.assertEqual(self.spider.data[2]['Headline'], "Headline 3")

    def test_extract_headlines_empty(self):
        """Test that empty or whitespace-only headlines are ignored."""
        mock_soup = MagicMock()

        # In the code, get_text(strip=True) is called.
        # We mock the return values to simulate empty/whitespace results after stripping.
        h1 = MagicMock()
        h1.get_text.return_value = ""
        h2 = MagicMock()
        h2.get_text.return_value = ""
        h3 = MagicMock()
        h3.get_text.return_value = "Valid Headline"

        mock_soup.find_all.return_value = [h1, h2, h3]

        self.spider.extract_data(mock_soup, "http://test.com")
        self.assertEqual(len(self.spider.data), 1)
        self.assertEqual(self.spider.data[0]['Headline'], "Valid Headline")

    def test_corporate_profile_selection(self):
        """Test corporate profile extraction logic with multiple candidates."""
        # The code tries 4 different selectors in order.
        # We test that it stops at the first successful one.

        mock_soup = MagicMock()

        # Scenario: first candidate (class 'corporate-profile') is found
        profile_el = MagicMock()
        profile_el.get_text.return_value = "Profile Content"
        mock_soup.find.return_value = profile_el

        self.spider.extract_data(mock_soup, "http://test.com")
        self.assertEqual(self.spider.corporate_profile, "Profile Content")
        # Ensure it didn't continue searching if first one found (though find is called multiple times in a list comprehension)
        # Actually in the code:
        # profile_candidates = [soup.find(...), soup.find(...), ...]
        # All soup.find calls are executed because they are in a list literal.
        self.assertGreaterEqual(mock_soup.find.call_count, 1)

    def test_corporate_profile_no_overwrite(self):
        """Test that corporate_profile is not overwritten if it is already set."""
        self.spider.corporate_profile = "Original Profile"
        mock_soup = MagicMock()

        self.spider.extract_data(mock_soup, "http://test.com")
        # find should not even be called for corporate profile if it's already set
        # (because of 'if not self.corporate_profile:')
        # Note: it might still be called for headlines.
        # But we check that corporate_profile remains unchanged.
        self.assertEqual(self.spider.corporate_profile, "Original Profile")

    def test_extract_data_no_matches(self):
        """Test extract_data with HTML that has no relevant tags."""
        mock_soup = MagicMock()
        mock_soup.find_all.return_value = []
        mock_soup.find.return_value = None

        self.spider.extract_data(mock_soup, "http://test.com")
        self.assertEqual(len(self.spider.data), 0)
        self.assertEqual(self.spider.corporate_profile, "")

if __name__ == '__main__':
    unittest.main()
