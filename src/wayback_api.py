from datetime import datetime
import time
from typing import Optional
import requests


def _query_all_available_snapshots(
    url: str,
    start_date: datetime,
    end_date: datetime,
    delay: float = 1.0
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

    response: requests.Response = requests.get(cdx_url, params=params, timeout=60)
    response.raise_for_status()

    # Be gentle with Internet Archive - add delay after request
    time.sleep(delay)

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
    delay: float = 1.0
) -> Optional[str]:
    """Find the first working snapshot for a URL on the wayback API

    Args:
        url: The URL to search for
        start_date: Start of date range
        end_date: End of date range
        delay: Seconds to wait after each request (default: 1.0)

    Returns:
        Archive.org URL of first working snapshot, or None if not found
    """
    snapshots: list[dict[str, str]] = _query_all_available_snapshots(
        url, start_date, end_date, delay=delay
    )

    for snapshot in snapshots:
        timestamp: str = snapshot["timestamp"]
        original_url: str = snapshot["url"]

        archive_url: str = f"https://web.archive.org/web/{timestamp}/{original_url}"

        try:
            response: requests.Response = requests.get(archive_url, timeout=30)
            response.raise_for_status()

            # Be gentle with Internet Archive - add delay after request
            time.sleep(delay)

            if _is_page_functional(response.text):
                return archive_url

        except requests.RequestException:
            # Still add delay even on error to avoid hammering the server
            time.sleep(delay)
            continue

    return None
