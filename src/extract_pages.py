"""Extract working versions of pages from Internet Archive"""

import re
import requests
import yaml
from datetime import datetime
from typing import Optional

from page import Page, PageType


def query_cdx_snapshots(
    url: str,
    start_date: datetime,
    end_date: datetime
) -> list[dict[str, str]]:
    """Query CDX API for snapshots of a URL within a date range

    Args:
        url: The URL to search for
        start_date: Start of date range (inclusive)
        end_date: End of date range (inclusive)

    Returns:
        List of snapshot dictionaries with timestamp and url
    """
    cdx_url: str = "http://web.archive.org/cdx/search/cdx"

    params: dict[str, str] = {
        "url": url,
        "from": start_date.strftime("%Y%m%d"),
        "to": end_date.strftime("%Y%m%d"),
        "output": "text",
        "filter": "statuscode:200",
    }

    response: requests.Response = requests.get(cdx_url, params=params, timeout=30)
    response.raise_for_status()

    start_timestamp: str = start_date.strftime("%Y%m%d%H%M%S")
    end_timestamp: str = end_date.strftime("%Y%m%d%H%M%S")

    snapshots: list[dict[str, str]] = []
    lines: list[str] = response.text.strip().split("\n")

    for line in lines:
        if not line:
            continue

        parts: list[str] = line.split()
        if len(parts) >= 3:
            timestamp: str = parts[1]
            original_url: str = parts[2]

            # Filter by timestamp range
            if start_timestamp <= timestamp <= end_timestamp:
                snapshots.append({
                    "timestamp": timestamp,
                    "url": original_url
                })

    return snapshots


def is_page_functional(html_content: str) -> bool:
    """Check if a page is functional (no MySQL error)

    Args:
        html_content: HTML content of the page

    Returns:
        True if page is functional, False otherwise
    """
    if not html_content or len(html_content.strip()) == 0:
        return False

    error_indicators: list[str] = [
        "Site under construction",
        "MySQL server",
        "technical problem (MySQL server)",
    ]

    content_lower: str = html_content.lower()

    for indicator in error_indicators:
        if indicator.lower() in content_lower:
            return False

    return True


def find_working_snapshot(
    url: str,
    start_date: datetime,
    end_date: datetime
) -> Optional[str]:
    """Find the first working snapshot for a URL

    Args:
        url: The URL to search for
        start_date: Start of date range
        end_date: End of date range

    Returns:
        Archive.org URL of first working snapshot, or None if not found
    """
    snapshots: list[dict[str, str]] = query_cdx_snapshots(url, start_date, end_date)

    for snapshot in snapshots:
        timestamp: str = snapshot["timestamp"]
        original_url: str = snapshot["url"]

        archive_url: str = f"https://web.archive.org/web/{timestamp}/{original_url}"

        try:
            response: requests.Response = requests.get(archive_url, timeout=30)
            response.raise_for_status()

            if is_page_functional(response.text):
                return archive_url

        except requests.RequestException:
            continue

    return None


def extract_timestamp_from_archive_url(archive_url: str) -> str:
    """Extract timestamp from an archive.org URL

    Args:
        archive_url: Archive.org URL containing timestamp

    Returns:
        Timestamp string (14 digits)

    Raises:
        ValueError: If timestamp cannot be extracted
    """
    pattern: str = r"web\.archive\.org/web/(\d{14})/"
    match: Optional[re.Match[str]] = re.search(pattern, archive_url)

    if match:
        return match.group(1)

    raise ValueError(f"Cannot extract timestamp from URL: {archive_url}")


def build_page(
    page_type: PageType,
    official_url: str,
    archive_url: str
) -> Page:
    """Build a Page object

    Args:
        page_type: Type of the page
        official_url: Original URL of the page
        archive_url: Archive.org URL of the page

    Returns:
        Page object with extracted information
    """
    timestamp: str = extract_timestamp_from_archive_url(archive_url)

    return Page(
        page_type=page_type,
        official_url=official_url,
        archive_url=archive_url,
        timestamp=timestamp,
    )


def extract_all_working_versions() -> Optional[Page]:
    """Extract all working versions from archive.org

    Returns:
        Homepage Page with nested pages and articles, or None if not found
    """
    start_date: datetime = datetime(2010, 1, 1)
    end_date: datetime = datetime(2015, 12, 31)

    # Extract homepage
    homepage_url: str = "https://www.sambre-marne-yser.be/sommaire.php3"
    homepage_archive: Optional[str] = find_working_snapshot(
        homepage_url, start_date, end_date
    )

    if not homepage_archive:
        return None

    homepage: Page = build_page(
        PageType.HOMEPAGE, homepage_url, homepage_archive
    )

    # Extract pages (01 to 99)
    for page_num in range(1, 100):
        page_url: str = (
            f"https://www.sambre-marne-yser.be/page_{page_num:02d}.php3"
        )

        page_archive: Optional[str] = find_working_snapshot(
            page_url, start_date, end_date
        )

        if page_archive:
            page: Page = build_page(PageType.PAGE, page_url, page_archive)
            homepage.add_child(page)

    return homepage


def save_to_yaml(page: Page, output_file: str) -> None:
    """Save page data to a YAML file

    Args:
        page: Page to save
        output_file: Path to output YAML file
    """
    data: dict[str, object] = page.to_dict()

    with open(output_file, "w", encoding="utf-8") as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True)


def main() -> None:
    """Main entry point"""
    print("Extracting pages from Internet Archive...")

    homepage: Optional[Page] = extract_all_working_versions()

    if not homepage:
        print("Error: Could not find homepage in archive")
        return

    output_file: str = "assets/pages.yaml"
    save_to_yaml(homepage, output_file)

    print(f"Pages saved to {output_file}")


if __name__ == "__main__":
    main()
