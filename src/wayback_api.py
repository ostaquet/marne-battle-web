from datetime import datetime
import os
from typing import Optional
import requests

from delay import wait_for


def _query_all_available_snapshots(
    url: str,
    start_date: datetime,
    end_date: datetime
) -> list[dict[str, str]]:
    """Query Wayback API for all snapshots of a URL within a date range

    Args:
        url: The URL to search for
        start_date: Start of date range (inclusive)
        end_date: End of date range (inclusive)
        delay: Seconds to wait after request (default: 1.0)

    Returns:
        List of snapshot dictionaries with timestamp and url
    """
    cdx_url: str = "https://web.archive.org/cdx/search/cdx"

    params: dict[str, str] = {
        "url": url,
        "from": start_date.strftime("%Y%m%d"),
        "to": end_date.strftime("%Y%m%d"),
        "output": "text",
        "filter": "statuscode:200",
    }

    print(f"Querying available snapshots on {cdx_url} for {url}...")
    text = _fetch_from_wayback(cdx_url, params)

    start_timestamp: str = start_date.strftime("%Y%m%d%H%M%S")
    end_timestamp: str = end_date.strftime("%Y%m%d%H%M%S")

    snapshots: list[dict[str, str]] = []
    lines: list[str] = text.strip().split("\n")

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


def _fetch_from_wayback(url: str, params: dict[str, str] = {},
                        max_retries: int = 3, timeout: int = 120,
                        delay_between_retry: int = 30) -> str:
    text: str = ""
    for i in range(max_retries):
        try:
            print("Fetch gently from {url}...")
            response: requests.Response = requests.get(url,
                                                       params=params,
                                                       timeout=timeout)
            response.raise_for_status()
            text = response.text
            print("  Succeed")
            break
        except requests.HTTPError as e:
            print(f"  Failed on {e.response}... Wait and retry...")
            wait_for(delay_between_retry)
            continue

    if text == "":
        raise requests.HTTPError()
    return text


def _is_page_functional(html_content: str) -> bool:
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
    end_date: datetime,
    delay_in_seconds: int
) -> Optional[str]:
    """Find the first working snapshot for a URL on the wayback API

    Args:
        url: The URL to search for
        start_date: Start of date range
        end_date: End of date range
        delay_in_seconds: Duration between two calls

    Returns:
        Archive.org URL of first working snapshot, or None if not found
    """
    snapshots: list[dict[str, str]] = _query_all_available_snapshots(
        url, start_date, end_date
    )

    for snapshot in snapshots:
        timestamp: str = snapshot["timestamp"]
        original_url: str = snapshot["url"]
        archive_url: str = f"https://web.archive.org/web/{timestamp}/{original_url}"

        text: str = _fetch_from_wayback(archive_url)

        # Be gentle with Internet Archive - add delay after request
        wait_for(delay_in_seconds)

        if _is_page_functional(text):
            return archive_url

    return None


def download_and_save_html(
    archive_url: str,
    output_dir: str,
    filename: str,
    delay_between_retry: int = 30
) -> bool:
    """Download HTML from archive.org and save to file

    Args:
        archive_url: Archive.org URL to download
        output_dir: Directory to save the file
        filename: Name of the output file

    Returns:
        True if successful, False otherwise
    """

    try:
        text: str = _fetch_from_wayback(archive_url,
                                        delay_between_retry=delay_between_retry)
    except requests.HTTPError:
        return False

    if text == "":
        return False

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Save the HTML content
    output_path: str = os.path.join(output_dir, filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    return True
