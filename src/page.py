"""Data structures for representing website pages"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, cast


class PageType(Enum):
    """Type of page in the website hierarchy"""

    HOMEPAGE = "homepage"
    PAGE = "page"
    ARTICLE = "article"


@dataclass
class Page:
    """Represents a page from the website

    Attributes:
        page_type: Type of the page (HOMEPAGE, PAGE, or ARTICLE)
        official_url: Original URL of the page
        archive_url: Archive.org URL of the page
        timestamp: Timestamp of the archive snapshot
        children: List of child pages
    """

    page_type: PageType
    official_url: str
    archive_url: str
    timestamp: str
    children: list["Page"] = field(default_factory=list)

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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Page":
        """Create a Page from dictionary representation

        Args:
            data: Dictionary containing page data

        Returns:
            Page instance created from the dictionary
        """
        page_type: PageType = PageType(str(data["type"]))
        official_url: str = str(data["official_url"])
        archive_url: str = str(data["archive_url"])
        timestamp: str = str(data["timestamp"])

        children_data: list[Any] = cast(
            list[Any], data.get("children", [])
        )
        children: list[Page] = [
            cls.from_dict(cast(dict[str, Any], child))
            for child in children_data
        ]

        return cls(
            page_type=page_type,
            official_url=official_url,
            archive_url=archive_url,
            timestamp=timestamp,
            children=children,
        )
