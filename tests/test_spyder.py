import unittest
from unittest.mock import patch, MagicMock
import os
import sys
# Add parent directory to path to import Corporate_SPYder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Corporate_SPYder import FinancialSpyder
import pandas as pd

class TestFinancialSpyder(unittest.TestCase):
    def setUp(self):
        self.csv_file = 'test_data.csv'
        self.pdf_file = 'test_report.pdf'
        self.spider = FinancialSpyder(
            start_url='http://test.com',
            ticker='TEST',
            csv_file=self.csv_file,
            pdf_file=self.pdf_file,
            max_depth=1,
            max_pages=2
        )
        self.spider.data = [] # Reset data
        self.spider.sentiment_scores = []
        self.spider.page_count = 0
        self.spider.corporate_profile = ""
        self.spider.visited = set()

    def tearDown(self):
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)
        if os.path.exists(self.pdf_file):
            os.remove(self.pdf_file)

    def test_analyze_sentiment(self):
        positive_text = "The market is booming and profits are good."
        negative_text = "The market is terrible and stocks are bad."
        neutral_text = "The market opened at 9 AM today."

        pos_score = self.spider.analyze_sentiment(positive_text)
        neg_score = self.spider.analyze_sentiment(negative_text)
        neu_score = self.spider.analyze_sentiment(neutral_text)

        self.assertGreater(pos_score, 0)
        self.assertLess(neg_score, 0)
        # Neutral might not be exactly 0 but close, let's assume exactly 0 for this simple sentence
        self.assertEqual(neu_score, 0)

    @patch('Corporate_SPYder.requests.get')
    def test_crawl(self, mock_get):
        # Mock response for start_url
        mock_response_1 = MagicMock()
        mock_response_1.content = b'''
            <html>
                <h1>Positive Market News</h1>
                <div class="corporate-profile">Test Company Profile</div>
                <a href="page2.html">Next Page</a>
            </html>
        '''
        mock_response_1.raise_for_status = MagicMock()

        # Mock response for page2.html
        mock_response_2 = MagicMock()
        mock_response_2.content = b'''
            <html>
                <h2>Another Headline</h2>
            </html>
        '''
        mock_response_2.raise_for_status = MagicMock()

        # Side effect to return different responses based on URL
        def side_effect(url, headers=None, timeout=None):
            if 'page2.html' in url:
                return mock_response_2
            return mock_response_1

        mock_get.side_effect = side_effect

        self.spider.crawl()

        # Verify pages crawled
        # Depending on how the queue works, it might try page2.html
        # Since I mocked page2.html content, it should extract from it too.
        # Max pages is 2.
        self.assertGreaterEqual(self.spider.page_count, 1)

        # Verify data extracted
        # Should have at least one headline
        self.assertGreaterEqual(len(self.spider.data), 1)
        self.assertEqual(self.spider.data[0]['Headline'], "Positive Market News")
        self.assertEqual(self.spider.corporate_profile, "Test Company Profile")

        # Verify sentiment stored
        self.assertGreaterEqual(len(self.spider.sentiment_scores), 1)

    def test_save_csv(self):
        self.spider.data = [
            {'Headline': 'Test Headline', 'Sentiment': 0.5, 'URL': 'http://test.com'}
        ]
        self.spider.save_csv()
        self.assertTrue(os.path.exists(self.csv_file))

        df = pd.read_csv(self.csv_file)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['Headline'], 'Test Headline')

    def test_generate_report(self):
        self.spider.data = [
            {'Headline': 'Positive News', 'Sentiment': 0.8, 'URL': 'http://test.com'},
            {'Headline': 'Negative News', 'Sentiment': -0.8, 'URL': 'http://test.com'}
        ]
        self.spider.sentiment_scores = [0.8, -0.8]
        self.spider.page_count = 1
        self.spider.generate_report()

        self.assertTrue(os.path.exists(self.pdf_file))

if __name__ == '__main__':
    unittest.main()
