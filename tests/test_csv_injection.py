import unittest
from unittest.mock import MagicMock
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock dependencies to avoid import errors
sys.modules['pandas'] = MagicMock()
sys.modules['fpdf'] = MagicMock()

from spyder_app.reporter import Reporter

class TestCSVInjection(unittest.TestCase):
    def setUp(self):
        # Reporter needs these arguments, but we only care about _sanitize_for_csv for this test
        self.reporter = Reporter("TEST", [], {}, [], "")

    def test_sanitize_basic(self):
        # Should sanitize basic dangerous characters
        self.assertEqual(self.reporter._sanitize_for_csv("=1+1"), "'=1+1")
        self.assertEqual(self.reporter._sanitize_for_csv("+1+1"), "'+1+1")
        self.assertEqual(self.reporter._sanitize_for_csv("-1+1"), "'-1+1")
        self.assertEqual(self.reporter._sanitize_for_csv("@SUM()"), "'@SUM()")

    def test_sanitize_whitespace_bypass(self):
        # Leading space bypasses current sanitization
        # Current code checks value[0] which is ' '
        self.assertEqual(self.reporter._sanitize_for_csv(" =1+1"), "' =1+1")
        self.assertEqual(self.reporter._sanitize_for_csv("\t=1+1"), "'\t=1+1")
        self.assertEqual(self.reporter._sanitize_for_csv("  @SUM()"), "'  @SUM()")

if __name__ == '__main__':
    unittest.main()
