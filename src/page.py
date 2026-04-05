from enum import Enum
import re
from typing import Any, Optional, cast


class PageType(Enum):
    """Type of page in the website hierarchy"""

    HOMEPAGE = "homepage"
    PAGE = "page"
    ARTICLE = "article"


class Page:
    """Represents a page from the website

    Attributes:
        page_type: Type of the page (HOMEPAGE, PAGE, or ARTICLE)
        official_url: Original URL of the page
        archive_url: Archive.org URL of the page
        timestamp: Timestamp of the archive snapshot
        children: List of child pages
    """

    def __init__(self, page_type: PageType, official_url: str, archive_url: str):
        timestamp: str = self._extract_timestamp_from_archive_url(archive_url)
        self.page_type = page_type
        self.official_url = official_url
        self.archive_url = archive_url
        self.timestamp = timestamp
        self.children: list[Page] = []

    def add_child(self, child: "Page") -> None:
        """Add a child page to this page

        Args:
            child: The child page to add
        """
        self.children.append(child)

    def to_dict(self) -> dict[str, object]:
        """Convert page to dictionary representation

        Returns:
            Dictionary representation of the page
        """
        return {
            "type": self.page_type.value,
            "official_url": self.official_url,
            "archive_url": self.archive_url,
            "timestamp": self.timestamp,
            "children": [child.to_dict() for child in self.children],
        }

    def _extract_timestamp_from_archive_url(self, archive_url: str) -> str:
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


def load_from_dict(data: dict[str, Any]) -> Page:
    page_type: PageType = PageType(str(data["type"]))
    official_url: str = str(data["official_url"])
    archive_url: str = str(data["archive_url"])

    current_page: Page = Page(
        page_type=page_type,
        official_url=official_url,
        archive_url=archive_url
    )

    children_data: list[Any] = cast(
        list[Any], data.get("children", [])
    )

    for child in children_data:
        current_page.add_child(load_from_dict(child))

    return current_page


class TestBuildPage:
    """Tests for building Page objects"""

    def test_build_page_creates_correct_structure(self) -> None:
        """Test that build_page creates correct Page structure"""
        official_url: str = (
            "https://www.sambre-marne-yser.be/sommaire.php3"
        )
        archive_url: str = (
            "https://web.archive.org/web/20131029060500/"
            "http://sambre-marne-yser.be/sommaire.php3"
        )

        page: Page = Page(
            PageType.HOMEPAGE,
            official_url=official_url,
            archive_url=archive_url
        )

        assert page.page_type == PageType.HOMEPAGE
        assert page.official_url == official_url
        assert page.archive_url == archive_url
        assert page.timestamp == "20131029060500"
        assert len(page.children) == 0
