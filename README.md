# Financial-spyder

A robust web crawler and financial analysis tool that extracts corporate data, performs sentiment analysis on headlines, fetches historical market data, and generates AI-ready market prediction briefings.

## Features

*   **Web Crawling**: Crawls websites to extract headlines and corporate profiles with depth and page limits.
*   **Historical Data Analysis**: Fetches maximum historical stock data using `yfinance` to "know every move the market ever made" for a given ticker.
*   **Technical Analysis**: Calculates key indicators like SMA (50/200), RSI, and Volatility Bands.
*   **Sentiment Analysis**: Analyzes extracted headlines using `TextBlob` to determine market sentiment.
*   **AI Analyst Integration**: Generates a detailed `ai_briefing.txt` prompt containing all gathered data (technicals + sentiment), optimized for LLMs (OpenAI Codex, Gemini, etc.) to predict future movement.
*   **Reporting**: Exports data to CSV and generates a comprehensive PDF report with summaries, technicals, and predictions.
*   **Automation Hook**: Includes `AI_Bot_Hook.py` to launch a browser and assist in feeding the briefing to an AI.

## Installation

1.  Clone the repository.
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: `playwright` is required for the bot hook. You may need to run `playwright install`.*
3.  (Optional) Download `TextBlob` corpora:
    ```bash
    python -m textblob.download_corpora
    ```

## Usage

### 1. Run the Spyder
This script gathers data, analyzes it, and generates the report and AI briefing.

```bash
python Corporate_SPYder.py
```

*   By default, it analyzes **SPY** (S&P 500 ETF) and crawls Yahoo Finance.
*   You can modify the `ticker` and `start_url` in the `if __name__ == "__main__":` block in `Corporate_SPYder.py`.

### 2. Use the AI Bot Hook
To get a "Zero Auth" style integration with OpenAI Codex or other AI tools:

```bash
python AI_Bot_Hook.py
```

1.  This launches a browser.
2.  Navigate to your preferred AI (e.g., OpenAI Codex).
3.  **Paste** the content (the script will guide you).
4.  The AI will act as a Senior Financial Analyst and provide a prediction based on the comprehensive data provided.

## Output

*   `financial_data.csv`: Scraped headlines and sentiment.
*   `market_report.pdf`: PDF report with technicals, sentiment, and summaries.
*   `ai_briefing.txt`: The "Perfect Prompt" containing all data for the AI.

## Testing

Run the unit tests:

```bash
python -m unittest discover tests
```

## Disclaimer

This tool is for informational purposes only and does not constitute financial advice. Market predictions are based on sentiment and technical indicators and should not be used for trading decisions.
