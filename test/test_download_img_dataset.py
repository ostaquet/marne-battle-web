"""Tests for downloading image dataset"""

import os
import hashlib
import responses
import yaml
from download_img_dataset import (
    extract_img_tags,
    build_archive_url,
    calculate_md5,
    process_html_files,
)


class TestExtractImgTags:
    """Tests for extracting img tags from HTML"""

    def test_extract_img_tags_from_html(self) -> None:
        """Test extracting img tags with src attributes"""
        img1_src: str = (
            "/web/20100516220948im_/"
            "http://www.sambre-marne-yser.be/IMG/jpg/bismarck.jpg"
        )
        img2_src: str = (
            "/web/20100516220950im_/"
            "http://www.sambre-marne-yser.be/IMG/jpg/photo.jpg"
        )
        html_content: str = f"""
        <html>
            <body>
                <img src="{img1_src}"/>
                <img src="{img2_src}"/>
                <p>Some text</p>
            </body>
        </html>
        """

        img_srcs: list[str] = extract_img_tags(html_content)

        assert len(img_srcs) == 2
        expected1: str = (
            "/web/20100516220948im_/"
            "http://www.sambre-marne-yser.be/IMG/jpg/bismarck.jpg"
        )
        expected2: str = (
            "/web/20100516220950im_/"
            "http://www.sambre-marne-yser.be/IMG/jpg/photo.jpg"
        )
        assert expected1 in img_srcs
        assert expected2 in img_srcs

    def test_extract_img_tags_returns_empty_for_no_images(self) -> None:
        """Test that HTML with no images returns empty list"""
        html_content: str = """
        <html>
            <body>
                <p>No images here</p>
            </body>
        </html>
        """

        img_srcs: list[str] = extract_img_tags(html_content)

        assert len(img_srcs) == 0


class TestBuildArchiveUrl:
    """Tests for building full archive URLs"""

    def test_build_archive_url_from_relative(self) -> None:
        """Test building full URL from relative path"""
        relative_url: str = (
            "/web/20100516220948im_/http://www.sambre-marne-yser.be/"
            "IMG/jpg/bismarck.jpg"
        )

        full_url: str = build_archive_url(relative_url)

        assert full_url == (
            "https://web.archive.org/web/20100516220948im_/"
            "http://www.sambre-marne-yser.be/IMG/jpg/bismarck.jpg"
        )

    def test_build_archive_url_from_absolute(self) -> None:
        """Test that absolute URLs are returned as-is"""
        absolute_url: str = (
            "https://web.archive.org/web/20100516220948im_/"
            "http://www.sambre-marne-yser.be/IMG/jpg/bismarck.jpg"
        )

        full_url: str = build_archive_url(absolute_url)

        assert full_url == absolute_url


class TestCalculateMd5:
    """Tests for MD5 calculation"""

    def test_calculate_md5_of_file(self, tmp_path) -> None:  # type: ignore
        """Test calculating MD5 hash of a file"""
        test_file = tmp_path / "test.jpg"
        test_file.write_bytes(b"test image content")

        md5_hash: str = calculate_md5(str(test_file))

        # MD5 of "test image content"
        expected: str = hashlib.md5(b"test image content").hexdigest()
        assert md5_hash == expected


class TestProcessHtmlFiles:
    """Tests for processing HTML files and building image map"""

    @responses.activate
    def test_process_html_files(self, tmp_path) -> None:  # type: ignore
        """Test processing HTML files and downloading images"""
        # Create HTML directory
        html_dir = tmp_path / "html"
        html_dir.mkdir()

        # Create a test HTML file
        html_file = html_dir / "test.htm"
        img_src: str = (
            "/web/20100516220948im_/"
            "http://www.sambre-marne-yser.be/IMG/jpg/photo1.jpg"
        )
        html_content: str = f"""
        <html>
            <body>
                <img src="{img_src}"/>
            </body>
        </html>
        """
        html_file.write_text(html_content)

        # Mock image download
        responses.add(
            responses.GET,
            (
                "https://web.archive.org/web/20100516220948im_/"
                "http://www.sambre-marne-yser.be/IMG/jpg/photo1.jpg"
            ),
            body=b"image data",
            status=200,
        )

        img_dir = tmp_path / "img"
        output_yaml = tmp_path / "img_map.yaml"

        # Process HTML files
        process_html_files(
            str(html_dir), str(img_dir), str(output_yaml), delay_between_calls=0
        )

        # Check that image was downloaded
        assert os.path.exists(os.path.join(img_dir, "photo1.jpg"))

        # Check that YAML was created
        assert os.path.exists(output_yaml)

        # Check YAML content
        with open(output_yaml, "r", encoding="utf-8") as f:
            img_map: dict[str, str] = yaml.safe_load(f)
            expected_url: str = (
                "/web/20100516220948im_/"
                "http://www.sambre-marne-yser.be/IMG/jpg/photo1.jpg"
            )
            assert expected_url in img_map
            assert img_map[expected_url] == "photo1.jpg"

    @responses.activate
    def test_process_handles_duplicate_filenames_same_content(
        self, tmp_path
    ) -> None:  # type: ignore
        """Test that duplicate filenames with same content are handled"""
        html_dir = tmp_path / "html"
        html_dir.mkdir()

        # Create two HTML files with same image filename
        html1 = html_dir / "page1.htm"
        html1.write_text(
            '<img src="/web/20100516220948im_/'
            'http://www.sambre-marne-yser.be/IMG/jpg/photo.jpg"/>'
        )

        html2 = html_dir / "page2.htm"
        html2.write_text(
            '<img src="/web/20100516220950im_/'
            'http://www.sambre-marne-yser.be/IMG/jpg/photo.jpg"/>'
        )

        # Mock both images with same content
        image_data: bytes = b"same image data"
        responses.add(
            responses.GET,
            (
                "https://web.archive.org/web/20100516220948im_/"
                "http://www.sambre-marne-yser.be/IMG/jpg/photo.jpg"
            ),
            body=image_data,
            status=200,
        )
        responses.add(
            responses.GET,
            (
                "https://web.archive.org/web/20100516220950im_/"
                "http://www.sambre-marne-yser.be/IMG/jpg/photo.jpg"
            ),
            body=image_data,
            status=200,
        )

        img_dir = tmp_path / "img"
        output_yaml = tmp_path / "img_map.yaml"

        process_html_files(
            str(html_dir), str(img_dir), str(output_yaml), delay_between_calls=0
        )

        # Both URLs should map to the same file
        with open(output_yaml, "r", encoding="utf-8") as f:
            img_map: dict[str, str] = yaml.safe_load(f)
            assert len(img_map) == 2
            assert img_map[
                "/web/20100516220948im_/http://www.sambre-marne-yser.be/"
                "IMG/jpg/photo.jpg"
            ] == "photo.jpg"
            assert img_map[
                "/web/20100516220950im_/http://www.sambre-marne-yser.be/"
                "IMG/jpg/photo.jpg"
            ] == "photo.jpg"
