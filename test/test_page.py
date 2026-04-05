"""Unit tests for page.py"""

from page import Page, PageType


class TestPageType:
    """Tests for PageType enum"""

    def test_page_type_has_homepage(self) -> None:
        """Test that PageType has HOMEPAGE value"""
        assert PageType.HOMEPAGE.value == "homepage"

    def test_page_type_has_page(self) -> None:
        """Test that PageType has PAGE value"""
        assert PageType.PAGE.value == "page"

    def test_page_type_has_article(self) -> None:
        """Test that PageType has ARTICLE value"""
        assert PageType.ARTICLE.value == "article"


class TestPage:
    """Tests for Page dataclass"""

    def test_create_page_without_children(self) -> None:
        """Test creating a page without children"""
        page: Page = Page(
            page_type=PageType.HOMEPAGE,
            official_url="https://www.sambre-marne-yser.be/sommaire.php3",
            archive_url=(
                "https://web.archive.org/web/20131029060500/"
                "http://sambre-marne-yser.be/sommaire.php3"
            ),
            timestamp="20131029060500",
        )

        assert page.page_type == PageType.HOMEPAGE
        assert (
            page.official_url
            == "https://www.sambre-marne-yser.be/sommaire.php3"
        )
        assert page.timestamp == "20131029060500"
        assert len(page.children) == 0

    def test_create_page_with_children(self) -> None:
        """Test creating a page with children"""
        child: Page = Page(
            page_type=PageType.ARTICLE,
            official_url=(
                "https://www.sambre-marne-yser.be/"
                "article=1.php3?id_article=1"
            ),
            archive_url=(
                "https://web.archive.org/web/20120101120000/"
                "http://www.sambre-marne-yser.be/article=1.php3?id_article=1"
            ),
            timestamp="20120101120000",
        )

        parent: Page = Page(
            page_type=PageType.PAGE,
            official_url="https://www.sambre-marne-yser.be/page_01.php3",
            archive_url=(
                "https://web.archive.org/web/20130101120000/"
                "http://www.sambre-marne-yser.be/page_01.php3"
            ),
            timestamp="20130101120000",
            children=[child],
        )

        assert len(parent.children) == 1
        assert parent.children[0] == child

    def test_add_child_to_page(self) -> None:
        """Test adding a child to a page"""
        parent: Page = Page(
            page_type=PageType.HOMEPAGE,
            official_url="https://www.sambre-marne-yser.be/sommaire.php3",
            archive_url=(
                "https://web.archive.org/web/20131029060500/"
                "http://sambre-marne-yser.be/sommaire.php3"
            ),
            timestamp="20131029060500",
        )

        child: Page = Page(
            page_type=PageType.PAGE,
            official_url="https://www.sambre-marne-yser.be/page_01.php3",
            archive_url=(
                "https://web.archive.org/web/20130101120000/"
                "http://www.sambre-marne-yser.be/page_01.php3"
            ),
            timestamp="20130101120000",
        )

        parent.add_child(child)

        assert len(parent.children) == 1
        assert parent.children[0] == child

    def test_page_to_dict(self) -> None:
        """Test converting page to dictionary"""
        page: Page = Page(
            page_type=PageType.HOMEPAGE,
            official_url="https://www.sambre-marne-yser.be/sommaire.php3",
            archive_url=(
                "https://web.archive.org/web/20131029060500/"
                "http://sambre-marne-yser.be/sommaire.php3"
            ),
            timestamp="20131029060500",
        )

        result: dict[str, object] = page.to_dict()

        assert result["type"] == "homepage"
        assert (
            result["official_url"]
            == "https://www.sambre-marne-yser.be/sommaire.php3"
        )
        assert result["timestamp"] == "20131029060500"
        assert result["children"] == []

    def test_page_to_dict_with_children(self) -> None:
        """Test converting page with children to dictionary"""
        child: Page = Page(
            page_type=PageType.ARTICLE,
            official_url=(
                "https://www.sambre-marne-yser.be/"
                "article=1.php3?id_article=1"
            ),
            archive_url=(
                "https://web.archive.org/web/20120101120000/"
                "http://www.sambre-marne-yser.be/article=1.php3?id_article=1"
            ),
            timestamp="20120101120000",
        )

        parent: Page = Page(
            page_type=PageType.PAGE,
            official_url="https://www.sambre-marne-yser.be/page_01.php3",
            archive_url=(
                "https://web.archive.org/web/20130101120000/"
                "http://www.sambre-marne-yser.be/page_01.php3"
            ),
            timestamp="20130101120000",
            children=[child],
        )

        result: dict[str, object] = parent.to_dict()

        assert result["type"] == "page"
        assert len(list(result["children"])) == 1
        child_dict: object = list(result["children"])[0]
        assert dict(child_dict)["type"] == "article"

    def test_page_from_dict(self) -> None:
        """Test creating page from dictionary"""
        data: dict[str, object] = {
            "type": "homepage",
            "official_url": "https://www.sambre-marne-yser.be/sommaire.php3",
            "archive_url": (
                "https://web.archive.org/web/20131029060500/"
                "http://sambre-marne-yser.be/sommaire.php3"
            ),
            "timestamp": "20131029060500",
            "children": [],
        }

        page: Page = Page.from_dict(data)

        assert page.page_type == PageType.HOMEPAGE
        assert (
            page.official_url
            == "https://www.sambre-marne-yser.be/sommaire.php3"
        )
        assert page.timestamp == "20131029060500"
        assert len(page.children) == 0

    def test_page_from_dict_with_children(self) -> None:
        """Test creating page with children from dictionary"""
        data: dict[str, object] = {
            "type": "page",
            "official_url": "https://www.sambre-marne-yser.be/page_01.php3",
            "archive_url": (
                "https://web.archive.org/web/20130101120000/"
                "http://www.sambre-marne-yser.be/page_01.php3"
            ),
            "timestamp": "20130101120000",
            "children": [
                {
                    "type": "article",
                    "official_url": (
                        "https://www.sambre-marne-yser.be/"
                        "article=1.php3?id_article=1"
                    ),
                    "archive_url": (
                        "https://web.archive.org/web/20120101120000/"
                        "http://www.sambre-marne-yser.be/"
                        "article=1.php3?id_article=1"
                    ),
                    "timestamp": "20120101120000",
                    "children": [],
                }
            ],
        }

        page: Page = Page.from_dict(data)

        assert page.page_type == PageType.PAGE
        assert len(page.children) == 1
        assert page.children[0].page_type == PageType.ARTICLE

    def test_page_roundtrip_to_dict_and_back(self) -> None:
        """Test converting page to dict and back preserves data"""
        original: Page = Page(
            page_type=PageType.HOMEPAGE,
            official_url="https://www.sambre-marne-yser.be/sommaire.php3",
            archive_url=(
                "https://web.archive.org/web/20131029060500/"
                "http://sambre-marne-yser.be/sommaire.php3"
            ),
            timestamp="20131029060500",
        )

        dict_repr: dict[str, object] = original.to_dict()
        restored: Page = Page.from_dict(dict_repr)

        assert restored.page_type == original.page_type
        assert restored.official_url == original.official_url
        assert restored.archive_url == original.archive_url
        assert restored.timestamp == original.timestamp
        assert len(restored.children) == len(original.children)
