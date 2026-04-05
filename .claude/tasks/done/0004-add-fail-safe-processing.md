# Problem to solve

When using `extract_articles.py`, we encounter some read timeout from the Internet Archive.

I suggest to:

1. Save the YAML file after each page processed.
2. If there are articles below a page, skip the page from the extraction process.
