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
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: Georgia, 'Times New Roman', serif;
            font-size: 17px;
            line-height: 1.75;
            color: #2c2c2c;
            background: #f5f0e8;
        }}

        header {{
            background: #1a1a2e;
            color: #e8dcc8;
            text-align: center;
            padding: 1.5rem 1rem;
            border-bottom: 3px solid #8b6914;
        }}

        header h1 {{
            font-size: 2rem;
            letter-spacing: 0.05em;
            font-weight: normal;
            text-transform: uppercase;
        }}

        header p {{
            font-size: 1rem;
            color: #c9a84c;
            margin-top: 0.25rem;
            letter-spacing: 0.1em;
        }}

        nav {{
            background: #2c2c2c;
            padding: 0;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}

        nav ul {{
            list-style: none;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            max-width: 1100px;
            margin: 0 auto;
            padding: 0 0.5rem;
        }}

        nav ul li a {{
            display: block;
            padding: 0.7rem 0.9rem;
            color: #e8dcc8;
            text-decoration: none;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 0.85rem;
            letter-spacing: 0.03em;
            transition: background 0.2s, color 0.2s;
            border-bottom: 3px solid transparent;
        }}

        nav ul li a:hover,
        nav ul li a.active {{
            color: #c9a84c;
            border-bottom-color: #c9a84c;
        }}

        main {{
            max-width: 820px;
            margin: 2.5rem auto;
            padding: 0 1.5rem 3rem;
        }}

        h1 {{
            font-size: 1.7rem;
            color: #1a1a2e;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #8b6914;
            font-weight: normal;
        }}

        h2 {{
            font-size: 1.35rem;
            color: #1a1a2e;
            margin-top: 2rem;
            margin-bottom: 0.75rem;
            font-weight: normal;
        }}

        h3 {{
            font-size: 1.1rem;
            color: #3a3a3a;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }}

        p {{
            margin-bottom: 1rem;
        }}

        a {{
            color: #6b4c11;
            text-decoration: underline;
        }}

        a:hover {{
            color: #8b6914;
        }}

        img {{
            display: block;
            max-width: 100%;
            height: auto;
            max-height: 480px;
            margin: 1.5rem auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.25);
        }}

        em {{
            display: block;
            text-align: center;
            font-style: italic;
            color: #666;
            font-size: 0.9rem;
            margin-top: -1rem;
            margin-bottom: 1.5rem;
        }}

        p > em:only-child {{
            display: block;
            text-align: center;
            font-style: italic;
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1.5rem 0;
            font-size: 0.9rem;
        }}

        th {{
            background: #1a1a2e;
            color: #e8dcc8;
            padding: 0.6rem 0.8rem;
            text-align: left;
        }}

        td {{
            padding: 0.5rem 0.8rem;
            border-bottom: 1px solid #d4c9b0;
        }}

        tr:nth-child(even) td {{
            background: #ede8dc;
        }}

        hr {{
            border: none;
            border-top: 1px solid #c9b99a;
            margin: 2rem 0;
        }}

        @media (max-width: 600px) {{
            header h1 {{ font-size: 1.4rem; }}
            nav ul li a {{ font-size: 0.75rem; padding: 0.6rem 0.5rem; }}
            main {{ padding: 0 1rem 2rem; }}
        }}
    </style>
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


def build_website(md_dir: str, img_dir: str, output_dir: str) -> None:
    """Build the full static website from Markdown and image sources."""
    os.makedirs(output_dir, exist_ok=True)

    md_files = [f for f in os.listdir(md_dir) if f.endswith(".md")]
    for md_file in md_files:
        md_path = os.path.join(md_dir, md_file)
        build_md_file(md_path, output_dir)

    copy_images(img_dir, output_dir)


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    build_website(
        md_dir=os.path.join(project_root, "assets", "md"),
        img_dir=os.path.join(project_root, "assets", "img"),
        output_dir=os.path.join(project_root, "assets", "build"),
    )
    print("Website built successfully in assets/build/")
