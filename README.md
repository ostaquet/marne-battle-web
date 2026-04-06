# marne-battle-web

Migration of https://www.sambre-marne-yser.be/ from Spip to Jekyll static website.

## Setup

Create a virtual environment and install dependencies:

```bash
./scripts/venv.sh
```

## Tools available

### Extracting pages from Internet Archive

The original website has a broken MySQL instance, making some pages inaccessible. We extract functional versions from the Internet Archive (2010-2015).

Run the extraction script:

```bash
source venv/bin/activate
python3 src/extract_pages.py
```

This will generate `assets/pages.yaml` containing the homepage and pages with their working archive.org URLs.

### Extracting articles from Internet Archive

After extracting pages, run the article extraction script to find and add article links:

```bash
source venv/bin/activate
python3 src/extract_articles.py
```

This will:

1. Read the `assets/pages.yaml` file
2. Download HTML from each page's archive URL
3. Extract article links from the HTML
4. Find working archive snapshots for each article
5. Generate `assets/articles.yaml` with the complete structure

## Development

### Running Tests

```bash
bash scripts/test.sh
```

### Running Linters

```bash
bash scripts/lint.sh
```

The project uses:

- **flake8** for code style (max line length: 88)
- **mypy** for type checking (strict mode)
