with open("tests/test_analyzer.py", "r") as f:
    content = f.read()

new_content = content.replace("import numpy as np", "")

with open("tests/test_analyzer.py", "w") as f:
    f.write(new_content)
