with open("spyder_app/crawler.py", "r") as f:
    content = f.read()

new_content = content.replace('''    GEOPOLITICAL_RE = re.compile("|".join(GEOPOLITICAL_KEYWORDS))
    ENVIRONMENTAL_RE = re.compile("|".join(ENVIRONMENTAL_KEYWORDS))''', '''    GEOPOLITICAL_RE = re.compile(r"\\b(" + "|".join(re.escape(kw) for kw in GEOPOLITICAL_KEYWORDS) + r")\\b", flags=re.IGNORECASE)
    ENVIRONMENTAL_RE = re.compile(r"\\b(" + "|".join(re.escape(kw) for kw in ENVIRONMENTAL_KEYWORDS) + r")\\b", flags=re.IGNORECASE)''')

with open("spyder_app/crawler.py", "w") as f:
    f.write(new_content)
