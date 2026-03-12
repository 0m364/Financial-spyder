import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock dependencies
sys.modules['pandas'] = MagicMock()
sys.modules['fpdf'] = MagicMock()

from spyder_app.reporter import Reporter

class TestReporter(unittest.TestCase):
    def setUp(self):
        self.data = [{'Headline': '=Test 1', 'Sentiment': 0.5, 'URL': 'http://test.com'}]
        self.technicals = {'Current_Price': 100, 'Prediction_Score': 80}
        self.sentiment_scores = [0.5]
        self.corporate_profile = "Test Profile"
        self.reporter = Reporter("TEST", self.data, self.technicals, self.sentiment_scores, self.corporate_profile)

    @patch('spyder_app.reporter.pd.DataFrame')
    def test_save_csv_sanitization(self, MockDF):
        mock_df_instance = MagicMock()
        MockDF.return_value = mock_df_instance

        self.reporter.save_csv("test.csv")

        # Verify sanitization logic
        expected_sanitized_data = [{'Headline': "'=Test 1", 'Sentiment': 0.5, 'URL': 'http://test.com'}]
        MockDF.assert_called_with(expected_sanitized_data)
        mock_df_instance.to_csv.assert_called_with('test.csv', index=False)

    @patch('spyder_app.reporter.FPDF')
    def test_generate_pdf_path_traversal(self, MockFPDF):
        mock_pdf_instance = MagicMock()
        MockFPDF.return_value = mock_pdf_instance

        # Try a path traversal attempt
        self.reporter.generate_pdf("../../../etc/passwd_report.pdf")

        # Verify filename was sanitized
        mock_pdf_instance.output.assert_called_with('passwd_report.pdf')

if __name__ == '__main__':
    unittest.main()
