import re

# Patch tests/test_ssrf_crawler.py
with open("tests/test_ssrf_crawler.py", "r") as f:
    content = f.read()

# Find the block under if __name__ == "__main__":
main_block = 'if __name__ == "__main__":\n    unittest.main()'
new_content = content.replace(main_block, "")
new_content += "\n" + main_block

with open("tests/test_ssrf_crawler.py", "w") as f:
    f.write(new_content)

# Patch tests/test_analyzer.py
with open("tests/test_analyzer.py", "r") as f:
    content = f.read()

main_block = 'if __name__ == "__main__":\n    unittest.main()'
new_content = content.replace(main_block, "")
new_content += "\n" + main_block

with open("tests/test_analyzer.py", "w") as f:
    f.write(new_content)
