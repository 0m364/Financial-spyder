with open("tests/test_analyzer.py", "r") as f:
    content = f.read()

new_content = content.replace("import pandas as pd", """
        import pandas as pd
        import sys
        sys.modules['pandas'] = pd""")

new_content = new_content.replace("""
        # Make the pandas dummy have an empty=False attribute
        df.empty = False
        self.analyzer.data = df""", """
        # Make the pandas dummy have an empty=False attribute
        df.empty = False
        self.analyzer.data = df
""")

with open("tests/test_analyzer.py", "w") as f:
    f.write(new_content)
