"""Tests for downloading HTML dataset locally"""

import os
import responses
from download_html_dataset import (
    generate_filename,
    download_and_save_html,
    build_local_dataset,
)
from page import Page, PageType


class TestGenerateFilename:
    """Tests for generating appropriate filenames"""

    def test_homepage_filename(self) -> None:
        """Test generating filename for homepage"""
        page: Page = Page(
            page_type=PageType.HOMEPAGE,
            official_url="https://www.sambre-marne-yser.be/sommaire.php3",
            archive_url=(
                "https://web.archive.org/web/20100110205213/"
                "http://www.sambre-marne-yser.be/sommaire.php3"
            ),
        )

        filename: str = generate_filename(page)

        assert filename == "homepage.htm"

    def test_page_filename(self) -> None:
        """Test generating filename for a page"""
        page: Page = Page(
            page_type=PageType.PAGE,
            official_url="https://www.sambre-marne-yser.be/page_02.php3",
            archive_url=(
                "https://web.archive.org/web/20100111045714/"
                "http://www.sambre-marne-yser.be/page_02.php3"
            ),
        )

        filename: str = generate_filename(page)

        assert filename == "page_02.htm"

    def test_article_filename(self) -> None:
        """Test generating filename for an article"""
        page: Page = Page(
            page_type=PageType.ARTICLE,
            official_url=(
                "https://www.sambre-marne-yser.be/"
                "article=2.php3?id_article=3"
            ),
            archive_url=(
                "https://web.archive.org/web/20100516221000/"
                "http://www.sambre-marne-yser.be/"
                "article=2.php3?id_article=3"
            ),
        )

        filename: str = generate_filename(page)

        assert filename == "article_02_03.htm"


class TestDownloadAndSaveHtml:
    """Tests for downloading and saving HTML files"""

    @responses.activate
    def test_download_and_save_creates_file(self, tmp_path) -> None:  # type: ignore
        """Test that HTML is downloaded and saved to file"""
        archive_url: str = (
            "https://web.archive.org/web/20100110205213/"
            "http://www.sambre-marne-yser.be/sommaire.php3"
        )
        html_content: str = "<html><body>Homepage</body></html>"

        responses.add(
            responses.GET,
            archive_url,
            body=html_content,
            status=200,
        )

        output_dir: str = str(tmp_path)
        filename: str = "homepage.htm"

        success: bool = download_and_save_html(
            archive_url,
            output_dir,
            filename,
            delay=0
        )

        assert success is True
        output_file: str = os.path.join(output_dir, filename)
        assert os.path.exists(output_file)

        with open(output_file, "r", encoding="utf-8") as f:
            content: str = f.read()
            assert content == html_content

    @responses.activate
    def test_download_handles_errors(self, tmp_path) -> None:  # type: ignore
        """Test that download errors are handled gracefully"""
        archive_url: str = (
            "https://web.archive.org/web/20100110205213/"
            "http://www.sambre-marne-yser.be/sommaire.php3"
        )

        responses.add(
            responses.GET,
            archive_url,
            status=404,
        )

        output_dir: str = str(tmp_path)
        filename: str = "homepage.htm"

        success: bool = download_and_save_html(
            archive_url,
            output_dir,
            filename,
            delay=0
        )

        assert success is False
        output_file: str = os.path.join(output_dir, filename)
        assert not os.path.exists(output_file)


class TestBuildLocalDataset:
    """Tests for building the complete local dataset"""

    @responses.activate
    def test_build_dataset_downloads_all_files(
        self, tmp_path
    ) -> None:  # type: ignore
        """Test that all files are downloaded and YAML is updated"""
        # Create a simple page structure
        homepage: Page = Page(
            page_type=PageType.HOMEPAGE,
            official_url="https://www.sambre-marne-yser.be/sommaire.php3",
            archive_url=(
                "https://web.archive.org/web/20100110205213/"
                "http://www.sambre-marne-yser.be/sommaire.php3"
            ),
        )

        page: Page = Page(
            page_type=PageType.PAGE,
            official_url="https://www.sambre-marne-yser.be/page_02.php3",
            archive_url=(
                "https://web.archive.org/web/20100111045714/"
                "http://www.sambre-marne-yser.be/page_02.php3"
            ),
        )
        homepage.add_child(page)

        # Mock HTTP responses
        responses.add(
            responses.GET,
            homepage.archive_url,
            body="<html><body>Homepage</body></html>",
            status=200,
        )
        responses.add(
            responses.GET,
            page.archive_url,
            body="<html><body>Page 2</body></html>",
            status=200,
        )

        output_dir: str = str(tmp_path)

        # Build the dataset
        build_local_dataset(homepage, output_dir, delay=0)

        # Check that files were created
        assert os.path.exists(os.path.join(output_dir, "homepage.htm"))
        assert os.path.exists(os.path.join(output_dir, "page_02.htm"))

        # Check that local_filename was added to pages
        assert hasattr(homepage, "local_filename")
        assert homepage.local_filename == "homepage.htm"
        assert hasattr(page, "local_filename")
        assert page.local_filename == "page_02.htm"
