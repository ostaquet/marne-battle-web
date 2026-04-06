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
            filename
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
            delay_between_retry=0
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
        build_local_dataset(homepage, output_dir, 
                            delay_between_retry=0, delay_between_calls=0)

        # Check that files were created
        assert os.path.exists(os.path.join(output_dir, "homepage.htm"))
        assert os.path.exists(os.path.join(output_dir, "page_02.htm"))

        # Check that local_filename was added to pages
        assert hasattr(homepage, "local_filename")
        assert homepage.local_filename == "homepage.htm"
        assert hasattr(page, "local_filename")
        assert page.local_filename == "page_02.htm"

    @responses.activate
    def test_build_dataset_skips_existing_files(
        self, tmp_path
    ) -> None:  # type: ignore
        """Test that existing files are not re-downloaded"""
        homepage: Page = Page(
            page_type=PageType.HOMEPAGE,
            official_url="https://www.sambre-marne-yser.be/sommaire.php3",
            archive_url=(
                "https://web.archive.org/web/20100110205213/"
                "http://www.sambre-marne-yser.be/sommaire.php3"
            ),
        )

        output_dir: str = str(tmp_path)

        # Create an existing file
        existing_file: str = os.path.join(output_dir, "homepage.htm")
        os.makedirs(output_dir, exist_ok=True)
        with open(existing_file, "w", encoding="utf-8") as f:
            f.write("<html><body>Existing content</body></html>")

        # Build the dataset - should skip the existing file
        # No HTTP mock needed since it shouldn't download
        build_local_dataset(homepage, output_dir, 
                            delay_between_retry=0, delay_between_calls=0)

        # Check that file still has original content (not downloaded)
        with open(existing_file, "r", encoding="utf-8") as f:
            content: str = f.read()
            assert content == "<html><body>Existing content</body></html>"

        # Check that local_filename was still added
        assert hasattr(homepage, "local_filename")
        assert homepage.local_filename == "homepage.htm"

    def test_build_dataset_with_progress_callback(
        self, tmp_path
    ) -> None:  # type: ignore
        """Test that progress callback is called after each download"""
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

        output_dir: str = str(tmp_path)

        # Create existing files so no HTTP calls are needed
        os.makedirs(output_dir, exist_ok=True)
        with open(
            os.path.join(output_dir, "homepage.htm"), "w", encoding="utf-8"
        ) as f:
            f.write("<html></html>")
        with open(
            os.path.join(output_dir, "page_02.htm"), "w", encoding="utf-8"
        ) as f:
            f.write("<html></html>")

        # Track progress callback calls
        progress_calls: list[Page] = []

        def progress_callback(page: Page) -> None:
            progress_calls.append(page)

        # Build the dataset with progress callback
        build_local_dataset(homepage, output_dir, 
                            delay_between_retry=0, delay_between_calls=0,
                            progress_callback=progress_callback)

        # Check that callback was called for each page
        assert len(progress_calls) == 2
        assert progress_calls[0] == homepage
        assert progress_calls[1] == page
