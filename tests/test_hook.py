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

from spyder_app.hook import hook_bot
from spyder_app import config

class TestHookBot(unittest.TestCase):
    @patch('builtins.open')
    @patch('spyder_app.hook.os.path.exists')
    @patch('builtins.print')
    def test_hook_bot_missing_prompt_file(self, mock_print, mock_exists, mock_open):
        """Test hook_bot missing prompt file."""
        # Arrange
        mock_exists.return_value = False

        # Act
        hook_bot()

        # Assert
        mock_exists.assert_called_once_with(config.AI_PROMPT_FILE)
        mock_print.assert_any_call(f"Error: '{config.AI_PROMPT_FILE}' not found. Run the Spyder first.")
        mock_open.assert_not_called()

if __name__ == '__main__':
    unittest.main()
