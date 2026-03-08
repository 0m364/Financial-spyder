import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock dependencies before importing spyder_app
sys.modules['playwright'] = MagicMock()
sys.modules['playwright.sync_api'] = MagicMock()

from spyder_app.hook import hook_bot
from spyder_app import config

class TestHookBot(unittest.TestCase):
    @patch('builtins.open')
    @patch('os.path.exists')
    @patch('builtins.print')
    def test_hook_bot_missing_prompt_file(self, mock_print, mock_exists, mock_open):
        # Configure mock to return False for os.path.exists
        mock_exists.return_value = False

        # Call the function
        hook_bot()

        # Verify os.path.exists was called with the correct file path
        mock_exists.assert_called_once_with(config.AI_PROMPT_FILE)

        # Verify the correct error message was printed
        expected_error_msg = f"Error: '{config.AI_PROMPT_FILE}' not found. Run the Spyder first."

        # We also print the header before checking if the file exists
        mock_print.assert_any_call("========================================")
        mock_print.assert_any_call("      AI BOT HOOK - AUTOMATION ASSIST   ")
        mock_print.assert_any_call("========================================")
        mock_print.assert_any_call(expected_error_msg)
        mock_open.assert_not_called()

if __name__ == '__main__':
    unittest.main()
