"""Extract article links from pages and populate the YAML structure"""

import re
import requests
import time
import yaml
from datetime import datetime
from typing import Any, Optional

from page import Page, PageType
from extract_pages import (
    find_working_snapshot,
    build_page,
)


def extract_article_links_from_html(html_content: str) -> list[str]:
    """Extract article links from HTML content

    Args:
        html_content: HTML content of a page

    Returns:
        List of article links (relative URLs)
    """
    pattern: str = r'href="([^"]*article=\d+\.php3\?id_article=\d+[^"]*)"'
    matches: list[str] = re.findall(pattern, html_content)

    # Extract just the relative part (article=X.php3?id_article=Y)
    article_links: set[str] = set()
    for match in matches:
        # Remove any absolute URL prefix
        if "article=" in match:
            # Extract the article=...php3?id_article=... part
            article_match: Optional[re.Match[str]] = re.search(
                r'(article=\d+\.php3\?id_article=\d+)', match
            )
            if article_match:
                article_links.add(article_match.group(1))

    return list(article_links)


def download_html_from_archive(
    archive_url: str,
    delay: float = 1.0
) -> str:
    """Download HTML content from an archive URL

    Args:
        archive_url: Archive.org URL to download
        delay: Seconds to wait after download (default: 1.0)

    Returns:
        HTML content, or empty string on error
    """
    try:
        response: requests.Response = requests.get(archive_url, timeout=30)
        response.raise_for_status()
        content: str = response.text

        # Be gentle with Internet Archive - add delay after request
        time.sleep(delay)

        return content
    except requests.RequestException:
        return ""


def load_page_from_yaml(yaml_file: str) -> Page:
    """Load a Page from a YAML file

    Args:
        yaml_file: Path to YAML file

    Returns:
        Page loaded from the file
    """
    with open(yaml_file, "r", encoding="utf-8") as file:
        data: Any = yaml.safe_load(file)

    return Page.from_dict(data)


def save_page_to_yaml(page: Page, yaml_file: str) -> None:
    """Save a Page to a YAML file

    Args:
        page: Page to save
        yaml_file: Path to output YAML file
    """
    data: dict[str, object] = page.to_dict()

    with open(yaml_file, "w", encoding="utf-8") as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True)


def process_page_for_articles(
    page: Page,
    start_date: datetime,
    end_date: datetime
) -> None:
    """Process a page to find and add article children

    Args:
        page: Page to process
        start_date: Start date for archive search
        end_date: End date for archive search
    """
    if page.page_type != PageType.PAGE:
        return

    # Skip pages that already have articles (fail-safe: resume capability)
    if len(page.children) > 0:
        print("  Skipping (already has articles)")
        return

    # Download HTML from the page's archive URL
    html_content: str = download_html_from_archive(page.archive_url)
    if not html_content:
        return

    # Extract article links
    article_links: list[str] = extract_article_links_from_html(html_content)

    # For each article link, find a working snapshot
    for article_link in article_links:
        # Build official URL
        official_url: str = (
            f"https://www.sambre-marne-yser.be/{article_link}"
        )

        # Find working snapshot
        archive_url: Optional[str] = find_working_snapshot(
            official_url, start_date, end_date
        )

        if archive_url:
            article: Page = build_page(
                PageType.ARTICLE,
                official_url,
                archive_url
            )
            page.add_child(article)


def extract_articles_from_pages(input_yaml: str, output_yaml: str) -> None:
    """Extract articles from pages and save updated structure

    Args:
        input_yaml: Path to input YAML file with pages
        output_yaml: Path to output YAML file with articles
    """
    start_date: datetime = datetime(2010, 1, 1)
    end_date: datetime = datetime(2015, 12, 31)

    # Load the homepage with pages
    homepage: Page = load_page_from_yaml(input_yaml)

    # Process each page to find articles
    for page in homepage.children:
        print(f"Processing {page.official_url}...")
        process_page_for_articles(page, start_date, end_date)
        print(f"  Found {len(page.children)} articles")

        # Save after each page (fail-safe: preserve progress)
        save_page_to_yaml(homepage, output_yaml)
        print(f"  Progress saved to {output_yaml}")

    print("All pages processed successfully")


def main() -> None:
    """Main entry point"""
    input_file: str = "assets/pages.yaml"
    output_file: str = "assets/articles.yaml"

    print("Extracting articles from pages...")
    extract_articles_from_pages(input_file, output_file)
    print(f"Articles saved to {output_file}")


if __name__ == "__main__":
    main()
