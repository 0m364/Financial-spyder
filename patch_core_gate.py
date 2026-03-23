with open("spyder_app/core.py", "r") as f:
    content = f.read()

new_content = content.replace("""        # Step 1: Historical Data
        self.analyzer.fetch_history(period=self.get_history_period())
        self.analyzer.calculate_indicators()""", """        # Step 1: Historical Data
        history_success = self.analyzer.fetch_history(period=self.get_history_period())
        if history_success and self.analyzer.data is not None and len(self.analyzer.data) >= 2:
            self.analyzer.calculate_indicators()
        else:
            print("Warning: Historical data fetch failed or returned insufficient data (< 2 rows). Technical analysis will be skipped.")
            self.analyzer.technicals['Incomplete_Report'] = True""")

new_content = new_content.replace("""    def perform_advanced_analysis(self):
        print("Performing Premium Analysis...")
        self.crawler.crawl_current_events()
        self.analyzer.calculate_premium_indicators()""", """    def perform_advanced_analysis(self):
        print("Performing Premium Analysis...")
        self.crawler.crawl_current_events()

        if self.analyzer.technicals.get('Incomplete_Report', False):
            print("Skipping premium indicators due to missing historical data.")
            return

        self.analyzer.calculate_premium_indicators()""")


with open("spyder_app/core.py", "w") as f:
    f.write(new_content)
