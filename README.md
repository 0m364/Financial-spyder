# Financial-spyder

A robust web crawler and financial analysis tool that extracts corporate data, performs sentiment analysis on headlines, fetches historical market data, and generates AI-ready market prediction briefings.

## Features

*   **Web Crawling**: Crawls websites to extract headlines and corporate profiles with depth and page limits.
*   **Historical Data Analysis**: Fetches maximum historical stock data using `yfinance` to "know every move the market ever made" for a given ticker.
*   **Technical Analysis**: Calculates key indicators like SMA (50/200), RSI, and Volatility Bands.
*   **Sentiment Analysis**: Analyzes extracted headlines to determine market sentiment.
*   **AI Analyst Integration**: Generates a detailed `ai_briefing.txt` prompt containing all gathered data (technicals + sentiment), optimized for LLMs (ChatGPT, Gemini, etc.) to predict future movement.
*   **Reporting**: Exports data to CSV and generates a comprehensive PDF report with summaries, technicals, and predictions.
*   **Browser Helper**: Includes `AI_Bot_Hook.py` / `hook.py` to launch a browser and assist in manually pasting the briefing to an AI tool.

## Installation

1.  Clone the repository.
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: `playwright` is required for the browser helper. You may need to run `playwright install`.*
3.  (Optional) Download `TextBlob` corpora:
    ```bash
    python -m textblob.download_corpora
    ```

## Usage

### 1. Run the Spyder
This script gathers data, analyzes it, and generates the report and AI briefing.

```bash
financial-spyder --url https://finance.yahoo.com --ticker SPY --tier premium
```

Alternatively, run the module directly:
```bash
python -m spyder_app.main --url https://finance.yahoo.com --ticker SPY
```

Options:
- `--url`: Start URL for crawling (default: https://finance.yahoo.com)
- `--ticker`: Ticker symbol (default: SPY)
- `--tier`: Usage tier, `free` or `premium` (default: free)
- `--hook`: Run the Browser Helper after analysis

*Note: The legacy script `Corporate_SPYder.py` is also available and uses configuration defaults.*

### 2. Use the Browser Helper
To get a browser-assisted automation hook with ChatGPT or other AI tools:

```bash
python AI_Bot_Hook.py
```
Or use the `--hook` flag with the main application.

1.  This launches a browser.
2.  Navigate to your preferred AI (e.g., ChatGPT).
3.  **Paste** the content (the script will guide you).
4.  The AI will act as a Senior Financial Analyst and provide a prediction based on the comprehensive data provided.

## Predictive Modeling Separation
The application uses standard technical analysis (SMA, RSI, MACD, etc.) to inform the main prediction score.
Experimental, casino-inspired prediction models (such as Martingale, Gambler's Fallacy, Fibonacci scaling, and Kelly Criterion proxy) are quarantined in an independent experimental scoring method. These experimental heuristics evaluate separately and do not contaminate the primary analytical prediction score.

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
