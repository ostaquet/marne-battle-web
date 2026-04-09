"""Tests for converting HTML files to Markdown"""

from convert_to_markdown import (
    convert_href,
    has_bullet_marker,
    extract_inline_text,
    convert_heading,
    convert_paragraph,
    convert_image_block,
    extract_table_row,
    convert_table,
    convert_html_to_markdown,
    convert_html_file,
)
from bs4 import BeautifulSoup


class TestConvertHref:
    """Tests for converting .htm hrefs to .md hrefs"""

    def test_convert_local_htm_link(self) -> None:
        """Test that .htm links are converted to .md"""
        assert convert_href("article_02_02.htm") == "article_02_02.md"

    def test_convert_homepage_link(self) -> None:
        """Test that homepage.htm is converted to homepage.md"""
        assert convert_href("homepage.htm") == "homepage.md"

    def test_preserve_external_links(self) -> None:
        """Test that non-.htm links are preserved"""
        assert convert_href("mailto:info@example.com") == "mailto:info@example.com"

    def test_preserve_image_paths(self) -> None:
        """Test that image paths are preserved"""
        assert convert_href("../img/photo.jpg") == "../img/photo.jpg"


class TestHasBulletMarker:
    """Tests for detecting spip_puce bullet markers"""

    def test_detects_puce_image(self) -> None:
        """Test detection of spip_puce image in paragraph"""
        html: str = '<p><img class="spip_puce" src="../img/puce.gif"/> Text</p>'
        soup = BeautifulSoup(html, "html.parser")
        p_tag = soup.find("p")
        assert has_bullet_marker(p_tag) is True

    def test_no_puce_image(self) -> None:
        """Test that paragraphs without puce images return False"""
        html: str = "<p>Regular paragraph</p>"
        soup = BeautifulSoup(html, "html.parser")
        p_tag = soup.find("p")
        assert has_bullet_marker(p_tag) is False


class TestExtractInlineText:
    """Tests for inline text extraction"""

    def test_extract_plain_text(self) -> None:
        """Test extracting plain text"""
        html: str = "<p>Simple text</p>"
        soup = BeautifulSoup(html, "html.parser")
        result: str = extract_inline_text(soup.find("p"))
        assert result == "Simple text"

    def test_extract_strong_text(self) -> None:
        """Test extracting bold text"""
        html: str = "<p><strong>Bold text</strong></p>"
        soup = BeautifulSoup(html, "html.parser")
        result: str = extract_inline_text(soup.find("p"))
        assert result == "**Bold text**"

    def test_extract_link(self) -> None:
        """Test extracting links with href conversion"""
        html: str = '<p><a href="page_02.htm">Page 2</a></p>'
        soup = BeautifulSoup(html, "html.parser")
        result: str = extract_inline_text(soup.find("p"))
        assert result == "[Page 2](page_02.md)"

    def test_extract_link_preserves_external(self) -> None:
        """Test that external links are preserved"""
        html: str = '<p><a href="mailto:info@example.com">Contact</a></p>'
        soup = BeautifulSoup(html, "html.parser")
        result: str = extract_inline_text(soup.find("p"))
        assert result == "[Contact](mailto:info@example.com)"

    def test_skip_puce_image(self) -> None:
        """Test that spip_puce images are skipped"""
        html: str = '<p><img class="spip_puce" src="../img/puce.gif"/> Text</p>'
        soup = BeautifulSoup(html, "html.parser")
        result: str = extract_inline_text(soup.find("p"))
        assert "puce.gif" not in result
        assert "Text" in result

    def test_extract_inline_image(self) -> None:
        """Test extracting non-puce inline images"""
        html: str = '<p><img alt="Photo" src="../img/photo.jpg"/></p>'
        soup = BeautifulSoup(html, "html.parser")
        result: str = extract_inline_text(soup.find("p"))
        assert result == "![Photo](../img/photo.jpg)"


class TestConvertHeading:
    """Tests for heading conversion"""

    def test_convert_h1(self) -> None:
        """Test h1 conversion"""
        html: str = "<h1>Main Title</h1>"
        soup = BeautifulSoup(html, "html.parser")
        result: str = convert_heading(soup.find("h1"))
        assert result == "# Main Title"

    def test_convert_h2(self) -> None:
        """Test h2 conversion"""
        html: str = "<h2>Section Title</h2>"
        soup = BeautifulSoup(html, "html.parser")
        result: str = convert_heading(soup.find("h2"))
        assert result == "## Section Title"

    def test_convert_h3_with_class(self) -> None:
        """Test h3 with SPIP class"""
        html: str = '<h3 class="spip">Sub Title</h3>'
        soup = BeautifulSoup(html, "html.parser")
        result: str = convert_heading(soup.find("h3"))
        assert result == "### Sub Title"


class TestConvertParagraph:
    """Tests for paragraph conversion"""

    def test_convert_regular_paragraph(self) -> None:
        """Test regular paragraph conversion"""
        html: str = "<p>Regular text content</p>"
        soup = BeautifulSoup(html, "html.parser")
        result: str = convert_paragraph(soup.find("p"))
        assert result == "Regular text content"

    def test_convert_bullet_paragraph(self) -> None:
        """Test bullet paragraph (with spip_puce) conversion"""
        html: str = (
            '<p class="spip">'
            '<img alt="-" class="spip_puce" src="../img/puce.gif"/>'
            "  Bullet point text"
            "</p>"
        )
        soup = BeautifulSoup(html, "html.parser")
        result: str = convert_paragraph(soup.find("p"))
        assert result.startswith("- ")
        assert "Bullet point text" in result
        assert "puce.gif" not in result

    def test_convert_paragraph_with_link(self) -> None:
        """Test paragraph with link conversion"""
        html: str = '<p><a href="article_02_02.htm">(Lire la suite...)</a></p>'
        soup = BeautifulSoup(html, "html.parser")
        result: str = convert_paragraph(soup.find("p"))
        assert "[" in result
        assert "article_02_02.md" in result


class TestConvertImageBlock:
    """Tests for image block conversion"""

    def test_convert_image_with_title_and_description(self) -> None:
        """Test full image block with title and description"""
        html: str = (
            '<div class="spip_documents spip_documents_center">'
            '<img alt="Bismarck" src="../img/bismarck.jpg"/>'
            '<div class="spip_doc_titre"><strong>Bismarck</strong></div>'
            '<div class="spip_doc_descriptif">Collection privée</div>'
            "</div>"
        )
        soup = BeautifulSoup(html, "html.parser")
        result: str = convert_image_block(soup.find("div"))
        assert "![Bismarck](../img/bismarck.jpg)" in result
        assert "_Bismarck_" in result
        assert "_Collection privée_" in result

    def test_convert_image_without_description(self) -> None:
        """Test image block without description"""
        html: str = (
            '<div class="spip_documents">'
            '<img alt="Photo" src="../img/photo.jpg"/>'
            '<div class="spip_doc_titre"><strong>Title</strong></div>'
            "</div>"
        )
        soup = BeautifulSoup(html, "html.parser")
        result: str = convert_image_block(soup.find("div"))
        assert "![Photo](../img/photo.jpg)" in result
        assert "_Title_" in result


class TestConvertTable:
    """Tests for table conversion"""

    def test_convert_table_with_header(self) -> None:
        """Test table with thead/tbody conversion"""
        html: str = """
        <table>
            <thead>
                <tr><th>Col A</th><th>Col B</th></tr>
            </thead>
            <tbody>
                <tr><td>Val 1</td><td>Val 2</td></tr>
                <tr><td>Val 3</td><td>Val 4</td></tr>
            </tbody>
        </table>
        """
        soup = BeautifulSoup(html, "html.parser")
        result: str = convert_table(soup.find("table"))
        assert "| Col A | Col B |" in result
        assert "| --- | --- |" in result
        assert "| Val 1 | Val 2 |" in result
        assert "| Val 3 | Val 4 |" in result

    def test_extract_table_row(self) -> None:
        """Test extracting cells from table row"""
        html: str = "<tr><td>Cell 1</td><td>Cell 2</td></tr>"
        soup = BeautifulSoup(html, "html.parser")
        cells: list[str] = extract_table_row(soup.find("tr"))
        assert cells == ["Cell 1", "Cell 2"]


class TestConvertHtmlToMarkdown:
    """Tests for full HTML to Markdown conversion"""

    def test_convert_article_html(self) -> None:
        """Test full conversion of article-like HTML"""
        html: str = """
        <html><body>
        <div id="main">
        <h1>Article Title</h1>
        <p class="spip">First paragraph with text.</p>
        <h3 class="spip">Sub Section</h3>
        <p class="spip">Second paragraph.</p>
        </div>
        </body></html>
        """
        result: str = convert_html_to_markdown(html)
        assert "# Article Title" in result
        assert "First paragraph with text." in result
        assert "### Sub Section" in result
        assert "Second paragraph." in result

    def test_convert_links_to_md(self) -> None:
        """Test that .htm links are converted to .md in output"""
        html: str = """
        <html><body>
        <div id="main">
        <p><a href="article_02_02.htm">(Lire la suite...)</a></p>
        </div>
        </body></html>
        """
        result: str = convert_html_to_markdown(html)
        assert "article_02_02.md" in result
        assert "article_02_02.htm" not in result

    def test_convert_image_links_preserved(self) -> None:
        """Test that image paths are preserved in output"""
        html: str = """
        <html><body>
        <div id="main">
        <div class="spip_documents spip_documents_center">
        <img alt="Photo" src="../img/photo.jpg"/>
        <div class="spip_doc_titre"><strong>Caption</strong></div>
        </div>
        </div>
        </body></html>
        """
        result: str = convert_html_to_markdown(html)
        assert "../img/photo.jpg" in result

    def test_convert_hr(self) -> None:
        """Test horizontal rule conversion"""
        html: str = """
        <html><body>
        <div id="main">
        <h2>Title</h2>
        <hr/>
        <h2>Another Title</h2>
        </div>
        </body></html>
        """
        result: str = convert_html_to_markdown(html)
        assert "---" in result

    def test_no_main_div_returns_empty(self) -> None:
        """Test that HTML without main div returns empty string"""
        html: str = "<html><body><p>Some content</p></body></html>"
        result: str = convert_html_to_markdown(html)
        assert result == ""


class TestConvertHtmlFile:
    """Tests for file-level HTML to Markdown conversion"""

    def test_converts_file_to_md(self, tmp_path) -> None:  # type: ignore
        """Test that HTML file is converted to .md file"""
        html_content: str = """
        <html><body>
        <div id="main">
        <h1>Test Title</h1>
        <p>Some content here.</p>
        </div>
        </body></html>
        """
        input_dir = tmp_path / "html"
        input_dir.mkdir()
        output_dir = tmp_path / "md"

        html_file = input_dir / "article_02_02.htm"
        html_file.write_text(html_content, encoding="utf-8")

        convert_html_file(str(html_file), str(output_dir))

        md_file = output_dir / "article_02_02.md"
        assert md_file.exists()
        content: str = md_file.read_text(encoding="utf-8")
        assert "# Test Title" in content
        assert "Some content here." in content
