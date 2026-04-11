"""Tests for building the static website from Markdown files."""

import os
import tempfile
from build_website import (
    md_filename_to_html_filename,
    extract_title,
    fix_image_paths,
    fix_md_links,
    clean_lire_la_suite,
    convert_image_links,
    wrap_images_with_lightbox,
    build_nav_items,
    convert_md_to_html,
    generate_html_page,
    build_md_file,
    copy_images,
    copy_stylesheet,
    build_website,
    NAVIGATION_ITEMS,
)


class TestMdFilenameToHtmlFilename:
    """Tests for converting Markdown filenames to HTML filenames."""

    def test_homepage_becomes_index(self) -> None:
        assert md_filename_to_html_filename("homepage.md") == "index.html"

    def test_homepage_with_path(self) -> None:
        assert md_filename_to_html_filename("/some/path/homepage.md") == "index.html"

    def test_page_file(self) -> None:
        assert md_filename_to_html_filename("page_02.md") == "page_02.html"

    def test_article_file(self) -> None:
        assert md_filename_to_html_filename("article_02_02.md") == "article_02_02.html"

    def test_article_with_path(self) -> None:
        result = md_filename_to_html_filename("/assets/md/article_04_07.md")
        assert result == "article_04_07.html"


class TestExtractTitle:
    """Tests for extracting the H1 title from Markdown content."""

    def test_extracts_first_h1(self) -> None:
        md = "# My Title\n\nSome content."
        assert extract_title(md) == "My Title"

    def test_ignores_h2(self) -> None:
        md = "## Subtitle\n\n# Real Title"
        assert extract_title(md) == "Real Title"

    def test_returns_default_when_no_h1(self) -> None:
        md = "## Only H2\n\nSome text."
        assert extract_title(md) == "Sambre-Marne-Yser"

    def test_trims_whitespace(self) -> None:
        md = "#   Spaced Title  \n\nContent."
        assert extract_title(md) == "Spaced Title"

    def test_real_homepage_title(self) -> None:
        md = '# Un site consacré à la phase "guerre de mouvement".'
        assert "Un site" in extract_title(md)


class TestFixImagePaths:
    """Tests for fixing ../img/ paths to img/ in HTML content."""

    def test_replaces_relative_img_path(self) -> None:
        html = '<img src="../img/photo.jpg" alt="Photo">'
        assert fix_image_paths(html) == '<img src="img/photo.jpg" alt="Photo">'

    def test_replaces_multiple_paths(self) -> None:
        html = '<img src="../img/a.jpg"><img src="../img/b.jpg">'
        result = fix_image_paths(html)
        assert '../img/' not in result
        assert 'img/a.jpg' in result
        assert 'img/b.jpg' in result

    def test_no_change_when_no_relative_path(self) -> None:
        html = '<img src="img/photo.jpg" alt="Photo">'
        assert fix_image_paths(html) == '<img src="img/photo.jpg" alt="Photo">'

    def test_leaves_other_content_unchanged(self) -> None:
        html = '<p>Some text with ../img/ in the text but not an attribute.</p>'
        result = fix_image_paths(html)
        assert 'img/' in result


class TestFixMdLinks:
    """Tests for converting .md href links to .html href links."""

    def test_converts_article_link(self) -> None:
        html = '<a href="article_02_02.md">Lire la suite</a>'
        assert fix_md_links(html) == '<a href="article_02_02.html">Lire la suite</a>'

    def test_converts_page_link(self) -> None:
        html = '<a href="page_03.md">Plans</a>'
        assert fix_md_links(html) == '<a href="page_03.html">Plans</a>'

    def test_converts_homepage_link(self) -> None:
        html = '<a href="homepage.md">Accueil</a>'
        assert fix_md_links(html) == '<a href="index.html">Accueil</a>'

    def test_multiple_links(self) -> None:
        html = '<a href="page_02.md">P2</a> <a href="article_03_04.md">Art</a>'
        result = fix_md_links(html)
        assert 'href="page_02.html"' in result
        assert 'href="article_03_04.html"' in result

    def test_external_links_unchanged(self) -> None:
        html = '<a href="https://example.com">External</a>'
        assert fix_md_links(html) == '<a href="https://example.com">External</a>'

    def test_no_md_links(self) -> None:
        html = '<p>Some text without links.</p>'
        assert fix_md_links(html) == '<p>Some text without links.</p>'


class TestCleanLireLaSuite:
    """Tests for cleaning up '(Lire la suite...)' link text."""

    def test_replaces_lire_la_suite_text(self) -> None:
        html = '<a href="article_02_02.html">(Lire la suite...)</a>'
        result = clean_lire_la_suite(html)
        assert ">Lire la suite<" in result
        assert "(Lire la suite...)" not in result

    def test_leaves_other_link_text_unchanged(self) -> None:
        html = '<a href="page_02.html">Prémisses</a>'
        assert clean_lire_la_suite(html) == html

    def test_handles_multiple_occurrences(self) -> None:
        html = (
            '<a href="a.html">(Lire la suite...)</a>'
            '<a href="b.html">(Lire la suite...)</a>'
        )
        result = clean_lire_la_suite(html)
        assert result.count("Lire la suite") == 2
        assert "(Lire la suite...)" not in result

    def test_no_change_when_no_match(self) -> None:
        html = "<p>Some text without any links.</p>"
        assert clean_lire_la_suite(html) == html


class TestConvertImageLinks:
    """Tests for converting anchor links pointing to images into <img> tags."""

    def test_converts_jpg_link(self) -> None:
        html = '<a href="img/map.jpg">Lien vers carte</a>'
        result = convert_image_links(html)
        assert '<img src="img/map.jpg" alt="Lien vers carte">' in result
        assert "<a" not in result

    def test_converts_png_link(self) -> None:
        html = '<a href="img/schema.png">Lien vers schéma</a>'
        result = convert_image_links(html)
        assert '<img src="img/schema.png"' in result

    def test_converts_gif_link(self) -> None:
        html = '<a href="img/anim.gif">Animation</a>'
        result = convert_image_links(html)
        assert '<img src="img/anim.gif"' in result

    def test_case_insensitive_extension(self) -> None:
        html = '<a href="img/photo.JPG">Photo</a>'
        result = convert_image_links(html)
        assert "<img" in result

    def test_leaves_html_links_unchanged(self) -> None:
        html = '<a href="page_02.html">Prémisses</a>'
        assert convert_image_links(html) == html

    def test_leaves_external_links_unchanged(self) -> None:
        html = '<a href="https://example.com">Example</a>'
        assert convert_image_links(html) == html

    def test_multiple_image_links(self) -> None:
        html = (
            '<a href="img/a.jpg">Map A</a>'
            '<a href="img/b.jpg">Map B</a>'
        )
        result = convert_image_links(html)
        assert 'src="img/a.jpg"' in result
        assert 'src="img/b.jpg"' in result
        assert "<a" not in result

    def test_preserves_alt_text(self) -> None:
        html = '<a href="img/marne.jpg">Carte de la Marne</a>'
        result = convert_image_links(html)
        assert 'alt="Carte de la Marne"' in result


class TestWrapImagesWithLightbox:
    """Tests for wrapping images in a CSS-only checkbox lightbox."""

    def test_wraps_img_in_label_zoom_link(self) -> None:
        html = '<img src="img/photo.jpg" alt="Photo">'
        result = wrap_images_with_lightbox(html)
        assert 'class="img-zoom-link"' in result
        assert 'for="img-chk-0"' in result

    def test_creates_hidden_checkbox(self) -> None:
        html = '<img src="img/photo.jpg" alt="Photo">'
        result = wrap_images_with_lightbox(html)
        assert 'type="checkbox"' in result
        assert 'id="img-chk-0"' in result
        assert 'class="img-zoom-toggle"' in result

    def test_creates_overlay_span(self) -> None:
        html = '<img src="img/photo.jpg" alt="Photo">'
        result = wrap_images_with_lightbox(html)
        assert 'class="img-zoom-overlay"' in result

    def test_overlay_contains_full_size_img(self) -> None:
        html = '<img src="img/map.jpg" alt="Map">'
        result = wrap_images_with_lightbox(html)
        assert result.count('src="img/map.jpg"') == 2

    def test_preserves_alt_in_overlay(self) -> None:
        html = '<img src="img/map.jpg" alt="Battle map">'
        result = wrap_images_with_lightbox(html)
        assert result.count('alt="Battle map"') == 2

    def test_no_change_when_no_images(self) -> None:
        html = "<p>Text without images.</p>"
        assert wrap_images_with_lightbox(html) == html

    def test_multiple_images_have_unique_ids(self) -> None:
        html = (
            '<img src="img/a.jpg" alt="A">'
            '<img src="img/b.jpg" alt="B">'
        )
        result = wrap_images_with_lightbox(html)
        assert 'id="img-chk-0"' in result
        assert 'id="img-chk-1"' in result
        assert 'for="img-chk-0"' in result
        assert 'for="img-chk-1"' in result

    def test_handles_self_closing_xhtml_img(self) -> None:
        html = '<img src="img/photo.jpg" alt="Photo" />'
        result = wrap_images_with_lightbox(html)
        assert 'class="img-zoom-link"' in result
        assert 'id="img-chk-0"' in result

    def test_overlay_close_uses_label_not_href(self) -> None:
        html = '<img src="img/photo.jpg" alt="Photo">'
        result = wrap_images_with_lightbox(html)
        assert 'href="#"' not in result
        assert 'for="img-chk-0"' in result


class TestBuildNavItems:
    """Tests for generating the navigation bar HTML."""

    def test_contains_all_nav_labels(self) -> None:
        nav = build_nav_items(None)
        for label, _ in NAVIGATION_ITEMS:
            assert label in nav

    def test_contains_all_nav_hrefs(self) -> None:
        nav = build_nav_items(None)
        for _, href in NAVIGATION_ITEMS:
            assert href in nav

    def test_active_class_on_matching_page(self) -> None:
        nav = build_nav_items("index.html")
        assert 'href="index.html" class="active"' in nav

    def test_no_active_class_on_other_pages(self) -> None:
        nav = build_nav_items("index.html")
        assert 'href="page_02.html" class="active"' not in nav

    def test_no_active_class_when_none(self) -> None:
        nav = build_nav_items(None)
        assert 'class="active"' not in nav


class TestConvertMdToHtml:
    """Tests for Markdown to HTML conversion."""

    def test_converts_heading(self) -> None:
        html = convert_md_to_html("# Hello")
        assert "<h1>Hello</h1>" in html

    def test_converts_paragraph(self) -> None:
        html = convert_md_to_html("Some text here.")
        assert "<p>" in html
        assert "Some text here." in html

    def test_converts_table(self) -> None:
        md = "| A | B |\n| --- | --- |\n| 1 | 2 |"
        html = convert_md_to_html(md)
        assert "<table>" in html
        assert "<td>" in html

    def test_converts_image(self) -> None:
        html = convert_md_to_html("![Alt text](../img/photo.jpg)")
        assert "<img" in html
        assert "photo.jpg" in html

    def test_converts_link(self) -> None:
        html = convert_md_to_html("[Lire la suite](article_02_02.md)")
        assert "<a" in html
        assert "article_02_02.md" in html


class TestGenerateHtmlPage:
    """Tests for generating the full HTML page from content and metadata."""

    def test_contains_header_title(self) -> None:
        html = generate_html_page("<p>Content</p>", "Test Title", None)
        assert "Sambre-Marne-Yser" in html

    def test_contains_subtitle(self) -> None:
        html = generate_html_page("<p>Content</p>", "Test Title", None)
        assert "Août - Novembre 1914" in html

    def test_contains_page_title(self) -> None:
        html = generate_html_page("<p>Content</p>", "My Page", None)
        assert "<title>My Page</title>" in html

    def test_contains_content(self) -> None:
        html = generate_html_page("<p>Hello World</p>", "Title", None)
        assert "Hello World" in html

    def test_contains_nav(self) -> None:
        html = generate_html_page("<p>Content</p>", "Title", None)
        assert "<nav>" in html

    def test_is_valid_html_structure(self) -> None:
        html = generate_html_page("<p>Content</p>", "Title", None)
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html

    def test_links_external_stylesheet(self) -> None:
        html = generate_html_page("<p>Content</p>", "Title", None)
        assert '<link rel="stylesheet" href="style.css">' in html
        assert "<style>" not in html


class TestBuildMdFile:
    """Tests for building a single HTML file from a Markdown file."""

    def test_creates_html_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            md_path = os.path.join(tmp_dir, "page_02.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write("# Prémisses\n\nSome content.")

            output_dir = os.path.join(tmp_dir, "build")
            os.makedirs(output_dir)
            build_md_file(md_path, output_dir)

            output_path = os.path.join(output_dir, "page_02.html")
            assert os.path.exists(output_path)

    def test_homepage_creates_index_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            md_path = os.path.join(tmp_dir, "homepage.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write("# Welcome\n\nSome text.")

            output_dir = os.path.join(tmp_dir, "build")
            os.makedirs(output_dir)
            build_md_file(md_path, output_dir)

            assert os.path.exists(os.path.join(output_dir, "index.html"))

    def test_output_contains_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            md_path = os.path.join(tmp_dir, "page_02.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write("# Prémisses\n\nUnique content for test.")

            output_dir = os.path.join(tmp_dir, "build")
            os.makedirs(output_dir)
            build_md_file(md_path, output_dir)

            out_path = os.path.join(output_dir, "page_02.html")
            with open(out_path, "r", encoding="utf-8") as f:
                html = f.read()

            assert "Unique content for test." in html
            assert "Sambre-Marne-Yser" in html

    def test_image_paths_are_fixed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            md_path = os.path.join(tmp_dir, "article_02_02.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write("# Article\n\n![Photo](../img/photo.jpg)\n")

            output_dir = os.path.join(tmp_dir, "build")
            os.makedirs(output_dir)
            build_md_file(md_path, output_dir)

            out_path = os.path.join(output_dir, "article_02_02.html")
            with open(out_path, "r", encoding="utf-8") as f:
                html = f.read()

            assert "../img/" not in html
            assert "img/photo.jpg" in html

    def test_md_links_are_converted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            md_path = os.path.join(tmp_dir, "page_02.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write("# Page\n\n[Lire](article_02_02.md)\n")

            output_dir = os.path.join(tmp_dir, "build")
            os.makedirs(output_dir)
            build_md_file(md_path, output_dir)

            out_path = os.path.join(output_dir, "page_02.html")
            with open(out_path, "r", encoding="utf-8") as f:
                html = f.read()

            assert 'href="article_02_02.html"' in html


class TestCopyImages:
    """Tests for copying images to the build directory."""

    def test_copies_images_to_img_subdir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            img_src = os.path.join(tmp_dir, "img_src")
            os.makedirs(img_src)
            open(os.path.join(img_src, "photo.jpg"), "w").close()
            open(os.path.join(img_src, "map.jpg"), "w").close()

            output_dir = os.path.join(tmp_dir, "build")
            os.makedirs(output_dir)
            copy_images(img_src, output_dir)

            assert os.path.exists(os.path.join(output_dir, "img", "photo.jpg"))
            assert os.path.exists(os.path.join(output_dir, "img", "map.jpg"))

    def test_overwrites_existing_img_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            img_src = os.path.join(tmp_dir, "img_src")
            os.makedirs(img_src)
            open(os.path.join(img_src, "new.jpg"), "w").close()

            output_dir = os.path.join(tmp_dir, "build")
            img_dst = os.path.join(output_dir, "img")
            os.makedirs(img_dst)
            open(os.path.join(img_dst, "old.jpg"), "w").close()

            copy_images(img_src, output_dir)

            assert os.path.exists(os.path.join(output_dir, "img", "new.jpg"))
            assert not os.path.exists(os.path.join(output_dir, "img", "old.jpg"))


class TestCopyStylesheet:
    """Tests for copying the CSS file to the build directory."""

    def test_copies_stylesheet_as_style_css(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            css_src = os.path.join(tmp_dir, "style.css")
            with open(css_src, "w", encoding="utf-8") as f:
                f.write("body { color: red; }")

            output_dir = os.path.join(tmp_dir, "build")
            os.makedirs(output_dir)
            copy_stylesheet(css_src, output_dir)

            assert os.path.exists(os.path.join(output_dir, "style.css"))

    def test_copied_content_matches_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            css_src = os.path.join(tmp_dir, "style.css")
            css_content = "body { background: #fff; }\nh1 { color: navy; }\n"
            with open(css_src, "w", encoding="utf-8") as f:
                f.write(css_content)

            output_dir = os.path.join(tmp_dir, "build")
            os.makedirs(output_dir)
            copy_stylesheet(css_src, output_dir)

            out_css = os.path.join(output_dir, "style.css")
            with open(out_css, "r", encoding="utf-8") as f:
                result = f.read()

            assert result == css_content


class TestBuildWebsite:
    """Integration tests for the full website build."""

    def _make_css(self, tmp_dir: str) -> str:
        """Create a minimal CSS file and return its path."""
        css_path = os.path.join(tmp_dir, "style.css")
        with open(css_path, "w", encoding="utf-8") as f:
            f.write("body { color: black; }")
        return css_path

    def test_builds_all_md_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            md_dir = os.path.join(tmp_dir, "md")
            img_dir = os.path.join(tmp_dir, "img")
            output_dir = os.path.join(tmp_dir, "build")
            os.makedirs(md_dir)
            os.makedirs(img_dir)
            css_path = self._make_css(tmp_dir)

            for name in ["homepage.md", "page_02.md", "article_02_02.md"]:
                with open(os.path.join(md_dir, name), "w", encoding="utf-8") as f:
                    f.write(f"# Title for {name}\n\nContent.")

            build_website(md_dir, img_dir, css_path, output_dir)

            assert os.path.exists(os.path.join(output_dir, "index.html"))
            assert os.path.exists(os.path.join(output_dir, "page_02.html"))
            assert os.path.exists(os.path.join(output_dir, "article_02_02.html"))

    def test_creates_img_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            md_dir = os.path.join(tmp_dir, "md")
            img_dir = os.path.join(tmp_dir, "img")
            output_dir = os.path.join(tmp_dir, "build")
            os.makedirs(md_dir)
            os.makedirs(img_dir)
            open(os.path.join(img_dir, "photo.jpg"), "w").close()
            css_path = self._make_css(tmp_dir)

            with open(os.path.join(md_dir, "homepage.md"), "w", encoding="utf-8") as f:
                f.write("# Home\n\nContent.")

            build_website(md_dir, img_dir, css_path, output_dir)

            assert os.path.exists(os.path.join(output_dir, "img", "photo.jpg"))

    def test_copies_stylesheet_to_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            md_dir = os.path.join(tmp_dir, "md")
            img_dir = os.path.join(tmp_dir, "img")
            output_dir = os.path.join(tmp_dir, "build")
            os.makedirs(md_dir)
            os.makedirs(img_dir)
            css_path = self._make_css(tmp_dir)

            with open(os.path.join(md_dir, "homepage.md"), "w", encoding="utf-8") as f:
                f.write("# Home\n\nContent.")

            build_website(md_dir, img_dir, css_path, output_dir)

            assert os.path.exists(os.path.join(output_dir, "style.css"))

    def test_creates_output_dir_if_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            md_dir = os.path.join(tmp_dir, "md")
            img_dir = os.path.join(tmp_dir, "img")
            output_dir = os.path.join(tmp_dir, "build", "nested")
            os.makedirs(md_dir)
            os.makedirs(img_dir)
            css_path = self._make_css(tmp_dir)

            with open(os.path.join(md_dir, "homepage.md"), "w", encoding="utf-8") as f:
                f.write("# Home\n\nContent.")

            build_website(md_dir, img_dir, css_path, output_dir)

            assert os.path.isdir(output_dir)
