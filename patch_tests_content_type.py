import re

# Patch test_spyder_app.py
with open("tests/test_spyder_app.py", "r") as f:
    content = f.read()

new_content = content.replace("            mock_response.iter_content.return_value = [\n                b\"<html><h1>Headline</h1></html>\"\n            ]", "            mock_response.iter_content.return_value = [\n                b\"<html><h1>Headline</h1></html>\"\n            ]\n            mock_response.headers = {'Content-Type': 'text/html'}")
new_content = new_content.replace("        with patch(\"spyder_app.crawler.requests.get\") as mock_get:\n            mock_response = MagicMock()\n            mock_response.iter_content.return_value = [\n                b\"<html><h1>Headline</h1></html>\"\n            ]\n            mock_response.headers.get.return_value = 'text/html'", "        with patch(\"spyder_app.crawler.requests.get\") as mock_get:\n            mock_response = MagicMock()\n            mock_response.iter_content.return_value = [\n                b\"<html><h1>Headline</h1></html>\"\n            ]\n            mock_response.headers = {'Content-Type': 'text/html'}")

with open("tests/test_spyder_app.py", "w") as f:
    f.write(new_content)
