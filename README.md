# Financial-spyder

A robust web crawler and financial analysis tool that extracts corporate data, performs sentiment analysis on headlines, and generates market prediction reports.

## Features

*   **Web Crawling**: Crawls websites to extract headlines and corporate profiles with depth and page limits.
*   **Sentiment Analysis**: Analyzes extracted headlines using `TextBlob` to determine market sentiment.
*   **Market Prediction**: Generates a "Bullish", "Bearish", or "Neutral" market outlook based on aggregated sentiment.
*   **Reporting**: Exports data to CSV and generates a comprehensive PDF report with summaries and predictions.
*   **Robustness**: Includes rate limiting, error handling, and user-agent rotation to respect server policies.

## Installation

1.  Clone the repository.
2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  (Optional) Download `TextBlob` corpora for advanced sentiment analysis (though basic works out of the box):
    ```bash
    python -m textblob.download_corpora
    ```

## Usage

Run the script directly:

```bash
python Corporate_SPYder.py
```

By default, it crawls `https://www.example.com`. You can modify the `start_url` in the `if __name__ == "__main__":` block at the bottom of `Corporate_SPYder.py`.

## Output

*   `financial_data.csv`: Contains extracted headlines, sentiment scores, and source URLs.
*   `market_report.pdf`: A PDF report summarizing the crawl, average sentiment, and market outlook.

## Testing

Run the unit tests to verify functionality:

```bash
python -m unittest discover tests
```

## Disclaimer

This tool is for informational purposes only and does not constitute financial advice. Market predictions are based on simple sentiment analysis and should not be used for trading decisions.
