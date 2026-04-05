"""Tests for loading real YAML files"""

import os
from extract_articles import load_page_from_yaml
from page import Page, PageType


class TestLoadRealYaml:
    """Tests for loading real generated YAML files"""

    def test_save_and_load_with_articles(self, tmp_path) -> None:  # type: ignore
        """Test saving and loading a Page with articles"""
        from extract_articles import save_page_to_yaml

        yaml_file = tmp_path / "test_articles.yaml"

        # Create a homepage with pages and articles
        homepage: Page = Page(
            page_type=PageType.HOMEPAGE,
            official_url="https://www.sambre-marne-yser.be/sommaire.php3",
            archive_url=(
                "https://web.archive.org/web/20131029060500/"
                "http://sambre-marne-yser.be/sommaire.php3"
            ),
        )

        # Add a page
        page: Page = Page(
            page_type=PageType.PAGE,
            official_url="https://www.sambre-marne-yser.be/page_01.php3",
            archive_url=(
                "https://web.archive.org/web/20130101120000/"
                "http://www.sambre-marne-yser.be/page_01.php3"
            ),
        )

        # Add articles to the page
        article1: Page = Page(
            page_type=PageType.ARTICLE,
            official_url=(
                "https://www.sambre-marne-yser.be/"
                "article=1.php3?id_article=1"
            ),
            archive_url=(
                "https://web.archive.org/web/20120101120000/"
                "http://www.sambre-marne-yser.be/"
                "article=1.php3?id_article=1"
            ),
        )

        article2: Page = Page(
            page_type=PageType.ARTICLE,
            official_url=(
                "https://www.sambre-marne-yser.be/"
                "article=1.php3?id_article=2"
            ),
            archive_url=(
                "https://web.archive.org/web/20120101120001/"
                "http://www.sambre-marne-yser.be/"
                "article=1.php3?id_article=2"
            ),
        )

        page.add_child(article1)
        page.add_child(article2)
        homepage.add_child(page)

        # Save to YAML
        save_page_to_yaml(homepage, str(yaml_file))

        # Load back from YAML
        loaded: Page = load_page_from_yaml(str(yaml_file))

        # Verify structure
        assert loaded.page_type == PageType.HOMEPAGE
        assert len(loaded.children) == 1
        assert loaded.children[0].page_type == PageType.PAGE
        assert len(loaded.children[0].children) == 2
        assert loaded.children[0].children[0].page_type == PageType.ARTICLE
        assert loaded.children[0].children[1].page_type == PageType.ARTICLE

    def test_load_pages_yaml(self) -> None:
        """Test loading the actual pages.yaml file"""
        pages_file: str = "assets/pages.yaml"

        # Skip test if file doesn't exist
        if not os.path.exists(pages_file):
            return

        # Try to load the file
        homepage: Page = load_page_from_yaml(pages_file)

        # Verify basic structure
        assert homepage.page_type == PageType.HOMEPAGE
        assert homepage.official_url == (
            "https://www.sambre-marne-yser.be/sommaire.php3"
        )
        assert len(homepage.children) > 0

        # Verify first child is a page
        first_page: Page = homepage.children[0]
        assert first_page.page_type == PageType.PAGE

    def test_load_articles_yaml(self) -> None:
        """Test loading the actual articles.yaml file"""
        articles_file: str = "assets/articles.yaml"

        # Skip test if file doesn't exist
        if not os.path.exists(articles_file):
            return

        # Try to load the file
        homepage: Page = load_page_from_yaml(articles_file)

        # Verify basic structure
        assert homepage.page_type == PageType.HOMEPAGE
        assert len(homepage.children) > 0
