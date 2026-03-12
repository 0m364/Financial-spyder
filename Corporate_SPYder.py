from spyder_app.core import FreeSpyder
from spyder_app import config

if __name__ == "__main__":
    print("Legacy entry point. Using Free Tier by default.")
    spider = FreeSpyder(
        start_url=config.DEFAULT_START_URL,
        ticker=config.DEFAULT_TICKER,
        csv_file=config.DEFAULT_CSV_FILE,
        pdf_file=config.DEFAULT_PDF_FILE,
    )
    spider.run()
