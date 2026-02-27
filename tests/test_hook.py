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
    @patch('spyder_app.hook.os.path.exists')
    @patch('builtins.print')
    def test_hook_bot_missing_prompt_file(self, mock_print, mock_exists):
        # Setup: Ensure os.path.exists returns False
        mock_exists.return_value = False

        # Action: Call hook_bot
        hook_bot()

        # Verification: Check if it correctly exited and printed the error
        mock_exists.assert_called_once_with(config.AI_PROMPT_FILE)
        mock_print.assert_any_call(f"Error: '{config.AI_PROMPT_FILE}' not found. Run the Spyder first.")

if __name__ == '__main__':
    unittest.main()
