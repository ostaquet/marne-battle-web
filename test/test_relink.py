"""Tests for relinking HTML files and images"""

import yaml
from relink import (
    extract_page_number,
    extract_article_numbers,
    relink_page_href,
    relink_img_src,
    relink_html_file,
    load_link_map,
)


class TestExtractPageNumber:
    """Tests for extracting page numbers from URLs"""

    def test_extract_page_number_from_page_url(self) -> None:
        """Test extracting page number from page_XX.php3"""
        url: str = "page_05.php3"
        page_num: str = extract_page_number(url)
        assert page_num == "05"

    def test_extract_page_number_with_path(self) -> None:
        """Test extracting page number from URL with path"""
        url: str = "/path/to/page_12.php3"
        page_num: str = extract_page_number(url)
        assert page_num == "12"

    def test_extract_page_number_returns_empty_for_invalid(self) -> None:
        """Test that invalid URLs return empty string"""
        url: str = "sommaire.php3"
        page_num: str = extract_page_number(url)
        assert page_num == ""


class TestExtractArticleNumbers:
    """Tests for extracting article numbers from URLs"""

    def test_extract_article_numbers(self) -> None:
        """Test extracting page and article numbers"""
        url: str = "article=5.php3?id_article=99"
        page_num, article_num = extract_article_numbers(url)
        assert page_num == "05"
        assert article_num == "99"

    def test_extract_article_numbers_with_path(self) -> None:
        """Test extracting with full path"""
        url: str = "/path/article=12.php3?id_article=456"
        page_num, article_num = extract_article_numbers(url)
        assert page_num == "12"
        assert article_num == "456"

    def test_extract_article_numbers_returns_empty_for_invalid(
        self
    ) -> None:
        """Test that invalid URLs return empty strings"""
        url: str = "page_05.php3"
        page_num, article_num = extract_article_numbers(url)
        assert page_num == ""
        assert article_num == ""


class TestLoadLinkMap:
    """Tests for loading link map from YAML"""

    def test_load_link_map_from_file(self, tmp_path) -> None:  # type: ignore
        """Test loading external links from YAML file"""
        link_map_file = tmp_path / "link_map.yaml"
        config: dict[str, list[str]] = {
            "external_links": [
                "http://www.spip.net/",
                "http://example.com/",
            ]
        }
        with open(link_map_file, "w", encoding="utf-8") as f:
            yaml.dump(config, f)

        external_links: list[str] = load_link_map(str(link_map_file))

        assert len(external_links) == 2
        assert "http://www.spip.net/" in external_links
        assert "http://example.com/" in external_links

    def test_load_link_map_returns_empty_for_missing_file(
        self
    ) -> None:
        """Test that missing file returns empty list"""
        external_links: list[str] = load_link_map("nonexistent.yaml")
        assert external_links == []

    def test_load_link_map_returns_empty_for_missing_key(
        self, tmp_path
    ) -> None:  # type: ignore
        """Test that missing external_links key returns empty list"""
        link_map_file = tmp_path / "link_map.yaml"
        config: dict[str, list[str]] = {"other_key": []}
        with open(link_map_file, "w", encoding="utf-8") as f:
            yaml.dump(config, f)

        external_links: list[str] = load_link_map(str(link_map_file))
        assert external_links == []


class TestRelinkPageHref:
    """Tests for relinking page hrefs"""

    def test_relink_homepage(self) -> None:
        """Test relinking to homepage"""
        href: str = "sommaire.php3"
        new_href: str = relink_page_href(href)
        assert new_href == "homepage.htm"

    def test_relink_homepage_with_path(self) -> None:
        """Test relinking homepage with path"""
        href: str = "/path/sommaire.php3"
        new_href: str = relink_page_href(href)
        assert new_href == "homepage.htm"

    def test_relink_homepage_with_archive_url(self) -> None:
        """Test relinking archive.org URL ending with root"""
        href: str = (
            "https://web.archive.org/web/20100417231020/"
            "http://www.sambre-marne-yser.be/"
        )
        new_href: str = relink_page_href(href)
        assert new_href == "homepage.htm"

    def test_relink_page(self) -> None:
        """Test relinking to page"""
        href: str = "page_05.php3"
        new_href: str = relink_page_href(href)
        assert new_href == "page_05.htm"

    def test_relink_article(self) -> None:
        """Test relinking to article"""
        href: str = "article=5.php3?id_article=99"
        new_href: str = relink_page_href(href)
        assert new_href == "article_05_99.htm"

    def test_relink_returns_empty_for_external(self) -> None:
        """Test that external links return empty string"""
        href: str = "http://example.com"
        new_href: str = relink_page_href(href)
        assert new_href == ""

    def test_relink_preserves_external_links_from_config(self) -> None:
        """Test that external links from config are preserved"""
        external_links: list[str] = [
            "http://www.spip.net/",
            "mailto:info@example.com",
        ]
        href1: str = (
            "https://web.archive.org/web/20100417230442/"
            "http://www.spip.net/"
        )
        href2: str = "mailto:info@example.com"

        new_href1: str = relink_page_href(href1, external_links)
        new_href2: str = relink_page_href(href2, external_links)

        assert new_href1 == "http://www.spip.net/"
        assert new_href2 == "mailto:info@example.com"


class TestRelinkImgSrc:
    """Tests for relinking image sources"""

    def test_relink_img_src(self) -> None:
        """Test relinking image src using map"""
        img_url: str = (
            "/web/20100417163745im_/"
            "http://www.sambre-marne-yser.be/IMG/jpg/photo.jpg"
        )
        img_map: dict[str, str] = {img_url: "photo.jpg"}
        new_src: str = relink_img_src(img_url, img_map)
        assert new_src == "../img/photo.jpg"

    def test_relink_img_src_returns_empty_for_not_found(self) -> None:
        """Test that unmapped images return empty string"""
        img_map: dict[str, str] = {}
        src: str = (
            "/web/20100417163745im_/"
            "http://www.sambre-marne-yser.be/IMG/jpg/missing.jpg"
        )
        new_src: str = relink_img_src(src, img_map)
        assert new_src == ""


class TestRelinkHtmlFile:
    """Tests for relinking complete HTML files"""

    def test_relink_html_file(self, tmp_path) -> None:  # type: ignore
        """Test relinking HTML file with pages and images"""
        # Create test HTML
        img_src: str = (
            "/web/20100417163745im_/"
            "http://www.sambre-marne-yser.be/IMG/jpg/photo.jpg"
        )
        html_content: str = f"""
        <html>
            <body>
                <a href="sommaire.php3">Home</a>
                <a href="page_05.php3">Page 5</a>
                <a href="article=5.php3?id_article=99">Article</a>
                <img src="{img_src}"/>
            </body>
        </html>
        """

        input_dir = tmp_path / "raw_html"
        output_dir = tmp_path / "html"
        input_dir.mkdir()
        output_dir.mkdir()

        input_file = input_dir / "test.htm"
        input_file.write_text(html_content)

        # Create image map
        img_map_file = tmp_path / "img_map.yaml"
        img_map: dict[str, str] = {img_src: "photo.jpg"}
        with open(img_map_file, "w", encoding="utf-8") as f:
            yaml.dump(img_map, f)

        log_file = tmp_path / "relink.log"

        # Relink the file
        relink_html_file(
            str(input_file),
            str(output_dir),
            img_map,
            str(log_file),
            []
        )

        # Check output file
        output_file = output_dir / "test.htm"
        assert output_file.exists()

        output_content: str = output_file.read_text()
        assert "homepage.htm" in output_content
        assert "page_05.htm" in output_content
        assert "article_05_99.htm" in output_content
        assert "../img/photo.jpg" in output_content

    def test_relink_logs_unmatched_links(self, tmp_path) -> None:  # type: ignore
        """Test that unmatched links are logged"""
        html_content: str = """
        <html>
            <body>
                <a href="http://example.com">External</a>
                <img src="/unknown/image.jpg"/>
            </body>
        </html>
        """

        input_dir = tmp_path / "raw_html"
        output_dir = tmp_path / "html"
        input_dir.mkdir()
        output_dir.mkdir()

        input_file = input_dir / "test.htm"
        input_file.write_text(html_content)

        log_file = tmp_path / "relink.log"

        # Relink the file
        relink_html_file(
            str(input_file),
            str(output_dir),
            {},
            str(log_file),
            []
        )

        # Check log file
        assert log_file.exists()
        log_content: str = log_file.read_text()
        assert "test.htm" in log_content
        assert "http://example.com" in log_content
        assert "/unknown/image.jpg" in log_content
