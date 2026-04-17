# Configuration for Financial Spyder

# Default settings
DEFAULT_START_URL = "https://finance.yahoo.com"
DEFAULT_TICKER = "SPY"
DEFAULT_CSV_FILE = "financial_data.csv"
DEFAULT_PDF_FILE = "market_report.pdf"

# Tier limits
FREE_MAX_DEPTH = 2
FREE_MAX_PAGES = 5
PREMIUM_MAX_DEPTH = 5
PREMIUM_MAX_PAGES = 20

# Technical Analysis Settings
SMA_SHORT = 50
SMA_LONG = 200
RSI_PERIOD = 14
BB_WINDOW = 20
BB_STD_DEV = 2

# Premium Analysis Settings
PREMIUM_HISTORY_LIMIT = "10y"
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
STOCH_WINDOW = 14
STOCH_SMOOTH = 3

# AI Prompt
AI_PROMPT_FILE = "ai_briefing.txt"
