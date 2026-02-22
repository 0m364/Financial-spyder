import argparse
from . import config
from .core import FreeSpyder, PremiumSpyder
from .hook import hook_bot

def main():
    parser = argparse.ArgumentParser(description="Financial Spyder - Corporate Analysis Tool")
    parser.add_argument('--url', type=str, default=config.DEFAULT_START_URL, help='Start URL for crawling')
    parser.add_argument('--ticker', type=str, default=config.DEFAULT_TICKER, help='Ticker symbol')
    parser.add_argument('--tier', type=str, choices=['free', 'premium'], default='free', help='Usage tier')
    parser.add_argument('--hook', action='store_true', help='Run the AI Bot Hook after analysis')

    args = parser.parse_args()

    print(f"Initializing Financial Spyder ({args.tier.capitalize()} Tier)...")

    spyder = None
    if args.tier == 'premium':
        spyder = PremiumSpyder(
            start_url=args.url,
            ticker=args.ticker,
            csv_file=config.DEFAULT_CSV_FILE,
            pdf_file=config.DEFAULT_PDF_FILE
        )
    else:
        spyder = FreeSpyder(
            start_url=args.url,
            ticker=args.ticker,
            csv_file=config.DEFAULT_CSV_FILE,
            pdf_file=config.DEFAULT_PDF_FILE
        )

    spyder.run()

    if args.hook:
        hook_bot()

if __name__ == "__main__":
    main()
