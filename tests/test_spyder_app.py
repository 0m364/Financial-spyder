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

# Now import the app
from spyder_app.core import FreeSpyder, PremiumSpyder
from spyder_app.crawler import WebCrawler
from spyder_app.analyzer import SentimentAnalyzer, TechnicalAnalyzer
from spyder_app.reporter import Reporter
from spyder_app import config

class TestSpyderApp(unittest.TestCase):
    def setUp(self):
        self.ticker = 'TEST'
        self.start_url = 'http://test.com'
        self.csv_file = 'test.csv'
        self.pdf_file = 'test.pdf'

    def test_free_spyder_init(self):
        spyder = FreeSpyder(self.start_url, self.ticker, self.csv_file, self.pdf_file)
        self.assertEqual(spyder.get_tier_name(), "Free")
        self.assertEqual(spyder.max_depth, config.FREE_MAX_DEPTH)
        self.assertEqual(spyder.get_history_period(), "1y")

    def test_premium_spyder_init(self):
        spyder = PremiumSpyder(self.start_url, self.ticker, self.csv_file, self.pdf_file)
        self.assertEqual(spyder.get_tier_name(), "Premium")
        self.assertEqual(spyder.max_depth, config.PREMIUM_MAX_DEPTH)
        self.assertEqual(spyder.get_history_period(), "max")

    def test_sentiment_analyzer(self):
        analyzer = SentimentAnalyzer()
        # Mock TextBlob
        with patch('spyder_app.analyzer.TextBlob') as MockTextBlob:
            instance = MockTextBlob.return_value
            instance.sentiment.polarity = 0.5
            score = analyzer.analyze("Good news")
            self.assertEqual(score, 0.5)

    @patch('spyder_app.crawler.is_safe_url')
    def test_web_crawler(self, mock_is_safe_url):
        mock_is_safe_url.return_value = True
        crawler = WebCrawler(self.start_url)

        # Mock requests.get
        with patch('spyder_app.crawler.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b'<html><h1>Headline</h1></html>'
            mock_response.is_redirect = False
            mock_get.return_value = mock_response

            # Mock BeautifulSoup
            with patch('spyder_app.crawler.BeautifulSoup') as MockBS:
                mock_soup = MagicMock()
                mock_headline = MagicMock()
                mock_headline.get_text.return_value = "Headline"

                # The mock setup for find_all is tricky because it's called with different args
                # Let's simplify and just rely on the fact that the code handles empty lists
                mock_soup.find_all.return_value = [mock_headline]
                # This will make crawl think [mock_headline] are links too, but since they don't have href, it should be fine?
                # Actually, if we return [mock_headline] for everything, the loop `for link in soup.find_all('a', href=True):`
                # will try to access link['href'].

                mock_headline.__getitem__ = MagicMock(return_value="http://test.com/next")

                # Mock SentimentAnalyzer
                with patch('spyder_app.crawler.SentimentAnalyzer') as MockSA:
                    crawler.sentiment_analyzer = MockSA.return_value
                    crawler.sentiment_analyzer.analyze.return_value = 0.8

                    # We need to ensure find_all behaves correctly for different calls
                    # But since we can't easily side_effect based on args with MagicMock simple setup
                    # Let's override extract_data for this test to avoid the complexity of mocking soup completely

                    crawler.extract_data = MagicMock()

                    # But we want to test extract_data integration?
                    # Let's skip the deep integration test of extract_data inside crawl
                    # and assume extract_data is unit tested separately (which it is in test_extract_data.py)
                    # So we just test that crawl calls extract_data

                    crawler.crawl()

                    crawler.extract_data.assert_called()

    def test_premium_analysis_logic(self):
        spyder = PremiumSpyder(self.start_url, self.ticker, self.csv_file, self.pdf_file)
        spyder.analyzer = MagicMock()
        spyder.analyzer.technicals = {
            'RSI': 20, # Oversold (+10)
            'Current_Price': 100,
            'SMA_200': 90, # Bullish (+10)
            'MACD': 0.5,
            'MACD_Signal': 0.4, # Bullish (+10)
        }
        spyder.crawler = MagicMock()
        spyder.crawler.sentiment_scores = [0.5, 0.6] # Bullish (+10)
        spyder.crawler.factors = {
            'Geopolitical': 0.0,
            'Environmental': 0.0,
            'Count_Geo': 0,
            'Count_Env': 0
        }

        # Initial Score 50 + 10 + 10 + 10 + 10 = 90

        spyder.perform_advanced_analysis()

        # Verify prediction score
        self.assertEqual(spyder.analyzer.technicals['Prediction_Score'], 90)

    def test_reporter(self):
        data = [{'Headline': 'H1', 'Sentiment': 0.5, 'URL': 'url'}]
        technicals = {'Current_Price': 100}
        sentiment = [0.5]
        profile = "Profile"

        reporter = Reporter('TEST', data, technicals, sentiment, profile)

        # Test CSV save
        with patch('spyder_app.reporter.pd.DataFrame') as MockDF:
            reporter.save_csv('test.csv')
            MockDF.return_value.to_csv.assert_called_with('test.csv', index=False)

        # Test PDF gen
        with patch('spyder_app.reporter.FPDF') as MockFPDF:
            reporter.generate_pdf('test.pdf')
            MockFPDF.return_value.output.assert_called_with('test.pdf')

            # Test Premium PDF gen
            reporter.technicals['Prediction_Score'] = 80
            reporter.generate_pdf('test_premium.pdf', tier='Premium')
            MockFPDF.return_value.output.assert_called_with('test_premium.pdf')

    def test_factor_tagging(self):
        crawler = WebCrawler(self.start_url)

        # Mock sentiment
        crawler.sentiment_analyzer = MagicMock()
        crawler.sentiment_analyzer.analyze.return_value = -0.5

        mock_soup = MagicMock()
        h1 = MagicMock()
        h1.get_text.return_value = "War in Region causes disaster"
        mock_soup.find_all.return_value = [h1]

        crawler.extract_data(mock_soup, self.start_url)

        self.assertEqual(crawler.factors['Count_Geo'], 1)
        self.assertEqual(crawler.factors['Count_Env'], 1) # 'disaster' is env keyword
        self.assertEqual(crawler.data[0]['Tags'], ['Geopolitical', 'Environmental'])

if __name__ == '__main__':
    unittest.main()
