"""Build a static website from Markdown files in assets/md/ and assets/img/."""

import os
import re
import shutil
from typing import Optional
import markdown

NAVIGATION_ITEMS: list[tuple[str, str]] = [
    ("Accueil", "index.html"),
    ("Prémisses", "page_02.html"),
    ("Plans et armées", "page_03.html"),
    ("Opérations", "page_04.html"),
    ("Batailles", "page_05.html"),
    ("Sièges", "page_06.html"),
    ("Combats", "page_07.html"),
    ("Epilogue", "page_08.html"),
    ("Annexes", "page_09.html"),
    ("Crédits", "page_10.html"),
]

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="style.css">
    <script src="scripts.js" defer></script>
</head>
<body>
    <header>
        <h1>Sambre-Marne-Yser</h1>
        <p>Août - Novembre 1914</p>
    </header>
    <nav>
        <ul>
{nav_items}
        </ul>
    </nav>
    <main>
{content}
    </main>
</body>
</html>
"""


def md_filename_to_html_filename(md_filename: str) -> str:
    """Convert a Markdown filename to its HTML output filename."""
    base = os.path.splitext(os.path.basename(md_filename))[0]
    if base == "homepage":
        return "index.html"
    return base + ".html"


def extract_title(md_content: str) -> str:
    """Extract the first H1 heading from Markdown content as the page title."""
    for line in md_content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return "Sambre-Marne-Yser"


def fix_image_paths(html_content: str) -> str:
    """Replace ../img/ references with img/ for the build output directory."""
    return html_content.replace("../img/", "img/")


def fix_md_links(html_content: str) -> str:
    """Replace .md href links with .html links, and homepage.md with index.html."""
    result = re.sub(
        r'href="([^"]*?)\.md"',
        _replace_md_href,
        html_content,
    )
    return result


def _replace_md_href(match: re.Match[str]) -> str:
    """Replace a single .md href with the corresponding .html filename."""
    base = match.group(1)
    if base == "homepage":
        return 'href="index.html"'
    return f'href="{base}.html"'


IMAGE_LINK_PATTERN = (
    r'<a href="([^"]+\.(?:jpg|jpeg|png|gif|webp))"[^>]*>([^<]*)</a>'
)

LIGHTBOX_CONTAINER_CLASS = "img-zoom-container"
LIGHTBOX_OVERLAY_CLASS = "img-zoom-overlay"


def clean_lire_la_suite(html_content: str) -> str:
    """Replace '(Lire la suite...)' link text with 'Lire la suite'."""
    return html_content.replace(">(Lire la suite...)<", ">Lire la suite<")


def convert_image_links(html_content: str) -> str:
    """Convert anchor links whose href points to an image into inline <img> tags."""
    return re.sub(
        IMAGE_LINK_PATTERN,
        lambda m: f'<img src="{m.group(1)}" alt="{m.group(2)}">',
        html_content,
        flags=re.IGNORECASE,
    )


def wrap_images_with_lightbox(html_content: str) -> str:
    """Wrap each image in a lightbox container for full-size viewing on click."""
    def make_lightbox(match: re.Match[str]) -> str:
        img_tag = match.group(0)
        src_match = re.search(r'\bsrc="([^"]*)"', img_tag)
        alt_match = re.search(r'\balt="([^"]*)"', img_tag)
        if not src_match:
            return img_tag
        src = src_match.group(1)
        alt = alt_match.group(1) if alt_match else ""
        return (
            f'<span class="{LIGHTBOX_CONTAINER_CLASS}">'
            f'{img_tag}'
            f'<span class="{LIGHTBOX_OVERLAY_CLASS}">'
            f'<img src="{src}" alt="{alt}"></span>'
            f'</span>'
        )

    return re.sub(r'<img\b[^>]*/?>',
                  make_lightbox, html_content)


def build_nav_items(active_html_filename: Optional[str]) -> str:
    """Build the HTML list items for the navigation bar."""
    items: list[str] = []
    for label, href in NAVIGATION_ITEMS:
        if href == active_html_filename:
            active = ' class="active"'
            items.append(f'            <li><a href="{href}"{active}>{label}</a></li>')
        else:
            items.append(f'            <li><a href="{href}">{label}</a></li>')
    return "\n".join(items)


def convert_md_to_html(md_content: str) -> str:
    """Convert Markdown content to an HTML fragment using the markdown library."""
    md = markdown.Markdown(extensions=["tables", "nl2br"])
    result: str = md.convert(md_content)
    return result


def generate_html_page(
    content_html: str,
    title: str,
    active_html_filename: Optional[str],
) -> str:
    """Wrap HTML content in the full page template with header and nav."""
    nav_items = build_nav_items(active_html_filename)
    indent = "        "
    indented_content = "\n".join(indent + line for line in content_html.splitlines())
    return HTML_TEMPLATE.format(
        title=title,
        nav_items=nav_items,
        content=indented_content,
    )


def build_md_file(
    md_path: str,
    output_dir: str,
) -> None:
    """Convert a single Markdown file to an HTML file in the output directory."""
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    title = extract_title(md_content)
    content_html = convert_md_to_html(md_content)
    content_html = fix_image_paths(content_html)
    content_html = fix_md_links(content_html)
    content_html = clean_lire_la_suite(content_html)
    content_html = convert_image_links(content_html)
    content_html = wrap_images_with_lightbox(content_html)

    output_filename = md_filename_to_html_filename(md_path)
    page_html = generate_html_page(content_html, title, output_filename)

    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(page_html)


def copy_images(img_src_dir: str, output_dir: str) -> None:
    """Copy all images from img_src_dir into output_dir/img/."""
    img_dst_dir = os.path.join(output_dir, "img")
    if os.path.exists(img_dst_dir):
        shutil.rmtree(img_dst_dir)
    shutil.copytree(img_src_dir, img_dst_dir)


def copy_stylesheet(css_src_path: str, output_dir: str) -> None:
    """Copy the CSS file into the output directory as style.css."""
    dst_path = os.path.join(output_dir, "style.css")
    shutil.copy2(css_src_path, dst_path)


def copy_scripts(js_src_path: str, output_dir: str) -> None:
    """Copy the JavaScript file into the output directory as scripts.js."""
    dst_path = os.path.join(output_dir, "scripts.js")
    shutil.copy2(js_src_path, dst_path)


def build_website(
    md_dir: str,
    img_dir: str,
    css_path: str,
    js_path: str,
    output_dir: str,
) -> None:
    """Build the full static website from Markdown and image sources."""
    os.makedirs(output_dir, exist_ok=True)

    md_files = [f for f in os.listdir(md_dir) if f.endswith(".md")]
    for md_file in md_files:
        md_path = os.path.join(md_dir, md_file)
        build_md_file(md_path, output_dir)

    copy_images(img_dir, output_dir)
    copy_stylesheet(css_path, output_dir)
    copy_scripts(js_path, output_dir)


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    build_website(
        md_dir=os.path.join(project_root, "assets", "md"),
        img_dir=os.path.join(project_root, "assets", "img"),
        css_path=os.path.join(project_root, "src", "style.css"),
        js_path=os.path.join(project_root, "src", "scripts.js"),
        output_dir=os.path.join(project_root, "assets", "build"),
    )
    print("Website built successfully in assets/build/")
