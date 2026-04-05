"""Unit tests for extract_articles.py"""

import responses
from extract_articles import (
    extract_article_links_from_html,
    load_page_from_yaml,
    save_page_to_yaml,
    download_html_from_archive,
)
from page import Page, PageType


class TestExtractArticleLinks:
    """Tests for extracting article links from HTML"""

    def test_extract_article_links_from_simple_html(self) -> None:
        """Test extracting article links from simple HTML"""
        html_content: str = """
        <html>
            <body>
                <a href="article=1.php3?id_article=5">Article 1</a>
                <a href="article=2.php3?id_article=10">Article 2</a>
                <a href="page_01.php3">Not an article</a>
            </body>
        </html>
        """

        links: list[str] = extract_article_links_from_html(html_content)

        assert len(links) == 2
        assert "article=1.php3?id_article=5" in links
        assert "article=2.php3?id_article=10" in links

    def test_extract_article_links_handles_absolute_urls(self) -> None:
        """Test extracting article links with absolute URLs"""
        html_content: str = """
        <html>
            <body>
                <a href="http://www.sambre-marne-yser.be/article=1.php3?id_article=5">
                    Article 1
                </a>
            </body>
        </html>
        """

        links: list[str] = extract_article_links_from_html(html_content)

        assert len(links) == 1
        assert "article=1.php3?id_article=5" in links

    def test_extract_article_links_returns_empty_for_no_articles(
        self
    ) -> None:
        """Test that no article links returns empty list"""
        html_content: str = """
        <html>
            <body>
                <a href="page_01.php3">Page 1</a>
                <a href="sommaire.php3">Homepage</a>
            </body>
        </html>
        """

        links: list[str] = extract_article_links_from_html(html_content)

        assert len(links) == 0

    def test_extract_article_links_deduplicates(self) -> None:
        """Test that duplicate article links are removed"""
        html_content: str = """
        <html>
            <body>
                <a href="article=1.php3?id_article=5">Article 1</a>
                <a href="article=1.php3?id_article=5">Article 1 again</a>
            </body>
        </html>
        """

        links: list[str] = extract_article_links_from_html(html_content)

        assert len(links) == 1


class TestDownloadHtml:
    """Tests for downloading HTML from archive"""

    @responses.activate
    def test_download_html_from_archive_returns_content(self) -> None:
        """Test downloading HTML from archive URL"""
        archive_url: str = (
            "https://web.archive.org/web/20130101120000/"
            "http://www.sambre-marne-yser.be/page_01.php3"
        )
        html_content: str = "<html><body>Test</body></html>"

        responses.add(
            responses.GET,
            archive_url,
            body=html_content,
            status=200,
        )

        result: str = download_html_from_archive(archive_url)

        assert result == html_content

    @responses.activate
    def test_download_html_handles_errors(self) -> None:
        """Test that download handles HTTP errors gracefully"""
        archive_url: str = (
            "https://web.archive.org/web/20130101120000/"
            "http://www.sambre-marne-yser.be/page_01.php3"
        )

        responses.add(
            responses.GET,
            archive_url,
            status=404,
        )

        result: str = download_html_from_archive(archive_url)

        assert result == ""


class TestLoadAndSaveYaml:
    """Tests for loading and saving YAML files"""

    def test_load_page_from_yaml(self, tmp_path) -> None:  # type: ignore
        """Test loading page from YAML file"""
        yaml_file = tmp_path / "test.yaml"
        archive_url_value: str = (
            "https://web.archive.org/web/20131029060500/"
            "http://sambre-marne-yser.be/sommaire.php3"
        )
        yaml_content: str = f"""
type: homepage
official_url: https://www.sambre-marne-yser.be/sommaire.php3
archive_url: {archive_url_value}
timestamp: '20131029060500'
children: []
        """
        yaml_file.write_text(yaml_content)

        page: Page = load_page_from_yaml(str(yaml_file))

        assert page.page_type == PageType.HOMEPAGE
        assert (
            page.official_url
            == "https://www.sambre-marne-yser.be/sommaire.php3"
        )
        assert page.timestamp == "20131029060500"

    def test_save_page_to_yaml(self, tmp_path) -> None:  # type: ignore
        """Test saving page to YAML file"""
        yaml_file = tmp_path / "output.yaml"

        page: Page = Page(
            page_type=PageType.HOMEPAGE,
            official_url="https://www.sambre-marne-yser.be/sommaire.php3",
            archive_url=(
                "https://web.archive.org/web/20131029060500/"
                "http://sambre-marne-yser.be/sommaire.php3"
            ),
            timestamp="20131029060500",
        )

        save_page_to_yaml(page, str(yaml_file))

        assert yaml_file.exists()
        content: str = yaml_file.read_text()
        assert "type: homepage" in content
        assert "timestamp: '20131029060500'" in content

    def test_roundtrip_load_and_save(self, tmp_path) -> None:  # type: ignore
        """Test that loading and saving preserves data"""
        yaml_file = tmp_path / "roundtrip.yaml"

        original: Page = Page(
            page_type=PageType.PAGE,
            official_url="https://www.sambre-marne-yser.be/page_01.php3",
            archive_url=(
                "https://web.archive.org/web/20130101120000/"
                "http://www.sambre-marne-yser.be/page_01.php3"
            ),
            timestamp="20130101120000",
        )

        save_page_to_yaml(original, str(yaml_file))
        loaded: Page = load_page_from_yaml(str(yaml_file))

        assert loaded.page_type == original.page_type
        assert loaded.official_url == original.official_url
        assert loaded.archive_url == original.archive_url
        assert loaded.timestamp == original.timestamp
