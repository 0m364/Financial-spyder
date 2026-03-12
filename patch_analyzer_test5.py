with open("tests/test_analyzer.py", "r") as f:
    content = f.read()

new_content = content.replace("""        # Make the pandas dummy have an empty=False attribute
        df.empty = False
        self.analyzer.data = df""", """        # We have to mock pandas correctly because it is mocked in sys.modules
        mock_df = MagicMock()
        mock_df.empty = False

        # Mock iloc to return dict-like objects
        latest = MagicMock()
        latest.__getitem__.side_effect = lambda k: {
            'Close': 100.0,
            'High': 105.0,
            'Low': 95.0,
            'SMA_50': 100.0,
            'SMA_200': 100.0,
            'RSI': 50.0,
            'BB_High': 105.0,
            'BB_Low': 95.0
        }[k]
        latest.name.strftime.return_value = '2020-01-01'

        prev = MagicMock()
        prev.__getitem__.side_effect = lambda k: {
            'Close': 100.0,
            'High': 105.0,
            'Low': 95.0,
        }[k]

        # Map iloc[-1] to latest and iloc[-2] to prev
        mock_iloc = MagicMock()
        mock_iloc.__getitem__.side_effect = lambda k: latest if k == -1 else prev
        mock_df.iloc = mock_iloc

        # Override the df variable completely to use this mock instead of the actual DataFrame since pandas is a Mock
        self.analyzer.data = mock_df""")

with open("tests/test_analyzer.py", "w") as f:
    f.write(new_content)
