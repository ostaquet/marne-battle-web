# marne-battle-web

Migration of https://www.sambre-marne-yser.be/ from Spip to Jekyll static website.

## Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Extracting Working Versions

The original website has a broken MySQL instance, making some pages inaccessible. We extract functional versions from the Internet Archive (2010-2015).

Run the extraction script:

```bash
source venv/bin/activate
export PYTHONPATH="$PWD/src:$PYTHONPATH"
python src/extract_working_versions.py
```

This will generate `working_versions.yaml` containing the homepage and pages with their working archive.org URLs.

## Extracting Articles

After extracting pages, run the article extraction script to find and add article links:

```bash
source venv/bin/activate
export PYTHONPATH="$PWD/src:$PYTHONPATH"
python src/extract_articles.py
```

This will:
1. Read the `working_versions.yaml` file
2. Download HTML from each page's archive URL
3. Extract article links from the HTML
4. Find working archive snapshots for each article
5. Generate `working_versions_with_articles.yaml` with the complete structure

## Data Structure

The project uses a strongly-typed `Page` dataclass to represent website pages:

```python
from page import Page, PageType

# Page attributes:
# - page_type: PageType (HOMEPAGE, PAGE, or ARTICLE)
# - official_url: str
# - archive_url: str
# - timestamp: str (14-digit archive timestamp)
# - children: list[Page]
```

This structure replaces the previous `dict[str, Any]` approach, providing better type safety and code clarity.

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

## Exploring the Internet Archive

Is a snapshot available on the Internet archive?

```bash
curl -X GET "https://archive.org/wayback/available?url=www.sambre-marne-yser.be"
```

How to get a list of available snapshots?

```bash
curl -X GET "http://web.archive.org/cdx/search/cdx?url=www.sambre-marne-yser.be"
```
