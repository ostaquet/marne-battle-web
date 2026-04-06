"""Download HTML files from archive.org and store them locally"""

import os
import re
import requests
import time
from typing import Optional

from page import Page, PageType
from extract_articles import load_page_from_yaml, save_page_to_yaml


def generate_filename(page: Page) -> str:
    """Generate appropriate filename for a page

    Args:
        page: Page object

    Returns:
        Filename for the page (e.g., "homepage.htm", "page_02.htm")
    """
    if page.page_type == PageType.HOMEPAGE:
        return "homepage.htm"

    elif page.page_type == PageType.PAGE:
        # Extract page number from URL (e.g., page_02.php3 -> 02)
        match: Optional[re.Match[str]] = re.search(
            r'page_(\d+)\.php3',
            page.official_url
        )
        if match:
            page_num: str = match.group(1)
            return f"page_{page_num}.htm"
        return "page_unknown.htm"

    elif page.page_type == PageType.ARTICLE:
        # Extract page and article numbers
        # Format: article=XX.php3?id_article=YY
        match = re.search(
            r'article=(\d+)\.php3\?id_article=(\d+)',
            page.official_url
        )
        if match:
            page_num = match.group(1).zfill(2)
            article_num: str = match.group(2).zfill(2)
            return f"article_{page_num}_{article_num}.htm"
        return "article_unknown.htm"

    return "unknown.htm"


def download_and_save_html(
    archive_url: str,
    output_dir: str,
    filename: str,
    delay: float = 1.0
) -> bool:
    """Download HTML from archive.org and save to file

    Args:
        archive_url: Archive.org URL to download
        output_dir: Directory to save the file
        filename: Name of the output file
        delay: Seconds to wait after download (default: 1.0)

    Returns:
        True if successful, False otherwise
    """
    try:
        response: requests.Response = requests.get(archive_url, timeout=30)
        response.raise_for_status()

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Save the HTML content
        output_path: str = os.path.join(output_dir, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(response.text)

        # Be gentle with Internet Archive
        time.sleep(delay)

        return True

    except requests.RequestException:
        # Still add delay even on error
        time.sleep(delay)
        return False


def build_local_dataset(
    homepage: Page,
    output_dir: str,
    delay: float = 1.0
) -> None:
    """Download all HTML files and add local_filename to each page

    Args:
        homepage: Root page with all children
        output_dir: Directory to save HTML files
        delay: Seconds to wait between downloads (default: 1.0)
    """
    def process_page(page: Page) -> None:
        """Process a single page and its children"""
        # Generate filename
        filename: str = generate_filename(page)

        # Download and save
        print(f"Downloading {page.archive_url}...")
        success: bool = download_and_save_html(
            page.archive_url,
            output_dir,
            filename,
            delay
        )

        if success:
            # Add local_filename attribute to the page
            page.local_filename = filename  # type: ignore
            print(f"  Saved as {filename}")
        else:
            print("  Failed to download")

        # Process children recursively
        for child in page.children:
            process_page(child)

    # Start processing from homepage
    process_page(homepage)


def main() -> None:
    """Main entry point"""
    input_file: str = "assets/articles.yaml"
    output_dir: str = "assets/raw_html"

    # Check if we should use pages.yaml instead
    if not os.path.exists(input_file):
        input_file = "assets/pages.yaml"

    print(f"Loading structure from {input_file}...")
    homepage: Page = load_page_from_yaml(input_file)

    print(f"Building local HTML dataset in {output_dir}...")
    build_local_dataset(homepage, output_dir)

    # Save updated YAML with local_filename fields
    output_yaml: str = "assets/dataset.yaml"
    save_page_to_yaml(homepage, output_yaml)
    print(f"Updated YAML saved to {output_yaml}")


if __name__ == "__main__":
    main()
