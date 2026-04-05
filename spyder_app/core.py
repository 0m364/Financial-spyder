from .crawler import WebCrawler
from .analyzer import TechnicalAnalyzer
from .reporter import Reporter
from . import config


class FinancialSpyder:
    def __init__(
        self,
        start_url,
        ticker,
        csv_file,
        pdf_file,
        max_depth=config.FREE_MAX_DEPTH,
        max_pages=config.FREE_MAX_PAGES,
    ):
        self.start_url = start_url
        self.ticker = ticker
        self.csv_file = csv_file
        self.pdf_file = pdf_file
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.crawler = None
        self.analyzer = None
        self.reporter = None

    def run(self):
        print(f"Starting Financial Spyder for {self.ticker}...")

        # Initialize components
        self.crawler = WebCrawler(self.start_url, self.max_depth, self.max_pages)
        self.analyzer = TechnicalAnalyzer(self.ticker)

        # Step 1: Historical Data
        history_success = self.analyzer.fetch_history(period=self.get_history_period())
        if history_success and self.analyzer.data is not None and len(self.analyzer.data) >= 2:
            self.analyzer.calculate_indicators()
        else:
            print("Warning: Historical data fetch failed or returned insufficient data (< 2 rows). Technical analysis will be skipped.")
            self.analyzer.technicals['Incomplete_Report'] = True

        # Step 2: Crawl
        self.crawler.crawl()

        self.perform_advanced_analysis()

        # Step 3: Report
        self.reporter = Reporter(
            self.ticker,
            self.crawler.data,
            self.analyzer.technicals,
            self.crawler.sentiment_scores,
            self.crawler.corporate_profile,
        )
        self.reporter.save_csv(self.csv_file)
        self.reporter.generate_pdf(self.pdf_file, tier=self.get_tier_name())
        self.reporter.generate_ai_prompt(config.AI_PROMPT_FILE, self.start_url)
        print("Done.")

    def get_history_period(self):
        return "1y"

    def perform_advanced_analysis(self):
        pass

    def get_tier_name(self):
        return "Base"


class FreeSpyder(FinancialSpyder):
    def get_history_period(self):
        return "1y"

    def get_tier_name(self):
        return "Free"


class PremiumSpyder(FinancialSpyder):
    def __init__(self, start_url, ticker, csv_file, pdf_file):
        super().__init__(
            start_url,
            ticker,
            csv_file,
            pdf_file,
            max_depth=config.PREMIUM_MAX_DEPTH,
            max_pages=config.PREMIUM_MAX_PAGES,
        )

    def get_history_period(self):
        return "max"

    def perform_advanced_analysis(self):
        print("Performing Premium Analysis...")
        self.crawler.crawl_current_events()

        if self.analyzer.technicals.get('Incomplete_Report', False):
            print("Skipping premium indicators due to missing historical data.")
            return

        self.analyzer.calculate_premium_indicators()

        # Proprietary Prediction Score
        # Simple algorithm: (RSI normalized + Sentiment + SMA trend) / 3
        technicals = self.analyzer.technicals

        score = 50  # Start neutral

        # RSI Contribution
        rsi = technicals.get("RSI", 50)
        if rsi < 30:
            score += 10  # Oversold -> Buy
        elif rsi > 70:
            score -= 10  # Overbought -> Sell

        # SMA Trend
        if technicals.get("Current_Price", 0) > technicals.get("SMA_200", 0):
            score += 10
        else:
            score -= 10

        # MACD
        if technicals.get("MACD", 0) > technicals.get("MACD_Signal", 0):
            score += 10
        else:
            score -= 10

        # Sentiment
        if self.crawler.sentiment_scores:
            avg_sentiment = sum(self.crawler.sentiment_scores) / len(
                self.crawler.sentiment_scores
            )
            if avg_sentiment > 0.1:
                score += 10
            elif avg_sentiment < -0.1:
                score -= 10

        # Factor Analysis Adjustment
        factors = self.crawler.factors
        if factors["Count_Geo"] > 0:
            geo_sentiment = factors["Geopolitical"] / factors["Count_Geo"]
            self.analyzer.technicals["Geopolitical_Score"] = geo_sentiment
            # Adjust prediction slightly based on geopolitical sentiment
            if geo_sentiment < -0.1:
                score -= 5
            elif geo_sentiment > 0.1:
                score += 5

        if factors["Count_Env"] > 0:
            env_sentiment = factors["Environmental"] / factors["Count_Env"]
            self.analyzer.technicals["Environmental_Score"] = env_sentiment
            # Adjust prediction slightly based on environmental sentiment
            if env_sentiment < -0.1:
                score -= 5
            elif env_sentiment > 0.1:
                score += 5

        # Store score
        self.analyzer.technicals["Prediction_Score"] = min(max(score, 0), 100)

        self._apply_experimental_models()

    def get_tier_name(self):
        return "Premium"

    def _apply_experimental_models(self):
        experimental_score = 50
        df = self.analyzer.data

        # --- EXPERIMENTAL CASINO PREDICTION MODELS ---
        experimental_score = self._apply_martingale_proxy(df, experimental_score)
        experimental_score = self._apply_gamblers_fallacy(df, experimental_score)
        experimental_score = self._apply_fibonacci_scaling(df, experimental_score)
        experimental_score = self._apply_kelly_criterion(df, experimental_score)
        # --- END EXPERIMENTAL MODELS ---

        self.analyzer.technicals["Experimental_Score"] = min(
            max(experimental_score, 0), 100
        )

    def _apply_martingale_proxy(self, df, score):
        """Martingale Proxy: If we lost yesterday, double down (increase score)."""
        if df is not None and not df.empty and len(df) >= 2:
            latest_close = df.iloc[-1]["Close"]
            prev_close = df.iloc[-2]["Close"]
            if latest_close < prev_close:
                score += 10  # Double down on the dip!
                self.analyzer.technicals["Martingale_Active"] = True
            else:
                self.analyzer.technicals["Martingale_Active"] = False
        return score

    def _apply_gamblers_fallacy(self, df, score):
        """Gambler's Fallacy (Monte Carlo Fallacy): 'It's gone down 3 days in a row, it HAS to go up now!'"""
        if df is not None and not df.empty and len(df) >= 4:
            c1 = df.iloc[-1]["Close"] < df.iloc[-2]["Close"]
            c2 = df.iloc[-2]["Close"] < df.iloc[-3]["Close"]
            c3 = df.iloc[-3]["Close"] < df.iloc[-4]["Close"]
            if c1 and c2 and c3:
                score += 20  # Overdue for a win!
                self.analyzer.technicals["Gamblers_Fallacy_Triggered"] = True
            else:
                self.analyzer.technicals["Gamblers_Fallacy_Triggered"] = False
        return score

    def _apply_fibonacci_scaling(self, df, score):
        """Fibonacci Sequence Scaling (Proxy): Scale based on consecutive losing days."""
        fib_seq = [1, 1, 2, 3, 5, 8, 13]
        if df is not None and not df.empty:
            consecutive_losses = 0
            for i in range(1, min(len(df), 8)):
                if df.iloc[-i]["Close"] < df.iloc[-(i + 1)]["Close"]:
                    consecutive_losses += 1
                else:
                    break
            if consecutive_losses > 0 and consecutive_losses < len(fib_seq):
                score += fib_seq[consecutive_losses] * 2  # Increase bet size
                self.analyzer.technicals["Fibonacci_Multiplier"] = fib_seq[
                    consecutive_losses
                ]
            else:
                self.analyzer.technicals["Fibonacci_Multiplier"] = 0
        return score

    def _apply_kelly_criterion(self, df, score):
        """Kelly Criterion Proxy: f* = p - (q / b)"""
        if df is not None and len(df) >= 30:
            last_30 = df.tail(30)
            wins = (last_30["Close"].diff() > 0).sum()
            p = wins / 30.0
            q = 1.0 - p
            # Assume b (odds) = 1 (even money payout for simplicity in this proxy)
            kelly_f = p - q
            # If kelly_f > 0, we have an edge. Scale score by it.
            if kelly_f > 0:
                score += kelly_f * 20  # Max 20 points from Kelly
            self.analyzer.technicals["Kelly_Criterion_f"] = kelly_f
        return score
