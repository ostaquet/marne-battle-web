"""Extract working versions of pages from Internet Archive"""

import requests
import yaml
from datetime import datetime
from typing import Optional


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


def build_page_entry(
    page_id: str,
    official_url: str,
    archive_url: str
) -> dict[str, str]:
    """Build a page entry for YAML output

    Args:
        page_id: ID of the page (e.g., 'homepage', 'page_01')
        official_url: Original URL of the page
        archive_url: Archive.org URL of the page

    Returns:
        Dictionary with page information
    """
    return {
        "id": page_id,
        "official_url": official_url,
        "archive_url": archive_url,
    }


def extract_all_working_versions() -> dict:
    """Extract all working versions from archive.org

    Returns:
        Dictionary structure with homepage, pages, and articles
    """
    start_date: datetime = datetime(2010, 1, 1)
    end_date: datetime = datetime(2015, 12, 31)

    result: dict = {}

    # Extract homepage
    homepage_url: str = "https://www.sambre-marne-yser.be/sommaire.php3"
    homepage_archive: Optional[str] = find_working_snapshot(
        homepage_url, start_date, end_date
    )

    if homepage_archive:
        result["homepage"] = build_page_entry(
            "homepage", homepage_url, homepage_archive
        )
        result["homepage"]["pages"] = []

    # Extract pages (01 to 99)
    for page_num in range(1, 100):
        page_id: str = f"page_{page_num:02d}"
        page_url: str = f"https://www.sambre-marne-yser.be/page_{page_num:02d}.php3"

        page_archive: Optional[str] = find_working_snapshot(
            page_url, start_date, end_date
        )

        if page_archive:
            page_entry: dict = build_page_entry(page_id, page_url, page_archive)
            page_entry["articles"] = []
            result["homepage"]["pages"].append(page_entry)

    return result


def save_to_yaml(data: dict, output_file: str) -> None:
    """Save data to a YAML file

    Args:
        data: Dictionary to save
        output_file: Path to output YAML file
    """
    with open(output_file, "w", encoding="utf-8") as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True)


def main() -> None:
    """Main entry point"""
    print("Extracting working versions from Internet Archive...")

    data: dict = extract_all_working_versions()

    output_file: str = "working_versions.yaml"
    save_to_yaml(data, output_file)

    print(f"Working versions saved to {output_file}")


if __name__ == "__main__":
    main()
