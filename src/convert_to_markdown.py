"""Convert HTML files to Markdown"""

import os
import re
from typing import Optional, Union
from bs4 import BeautifulSoup, Tag, NavigableString, PageElement


def convert_href(href: str) -> str:
    """Convert .htm href to .md href for local links

    Args:
        href: Original href attribute value

    Returns:
        Converted href with .md extension for local files
    """
    if href.endswith(".htm"):
        return href[:-4] + ".md"
    return href


def has_bullet_marker(p_tag: Tag) -> bool:
    """Check if paragraph starts with a spip_puce bullet image

    Args:
        p_tag: Paragraph tag to check

    Returns:
        True if the paragraph contains a spip_puce image
    """
    return bool(p_tag.find("img", class_="spip_puce"))


def extract_inline_text(element: Tag) -> str:
    """Extract inline text from element, converting inline HTML to Markdown

    Args:
        element: HTML tag to extract text from

    Returns:
        Markdown-formatted inline text
    """
    result: str = ""
    child: PageElement
    for child in element.children:
        if isinstance(child, NavigableString):
            result += str(child)
        elif isinstance(child, Tag):
            if child.name in ("strong", "b"):
                inner: str = extract_inline_text(child)
                result += f"**{inner.strip()}**"
            elif child.name in ("em", "i"):
                inner = extract_inline_text(child)
                result += f"*{inner.strip()}*"
            elif child.name == "a":
                href: str = str(child.get("href", ""))
                text: str = extract_inline_text(child)
                result += f"[{text}]({convert_href(href)})"
            elif child.name == "img":
                css_class: Union[str, list[str]] = child.get("class", [])
                if "spip_puce" not in css_class:
                    alt: str = str(child.get("alt", ""))
                    src: str = str(child.get("src", ""))
                    result += f"![{alt}]({src})"
            else:
                result += extract_inline_text(child)
    return result


def convert_heading(tag: Tag) -> str:
    """Convert heading tag to Markdown heading

    Args:
        tag: Heading tag (h1-h6)

    Returns:
        Markdown heading string
    """
    level: int = int(tag.name[1])
    prefix: str = "#" * level
    text: str = tag.get_text(strip=True)
    return f"{prefix} {text}"


def convert_paragraph(tag: Tag) -> str:
    """Convert paragraph tag to Markdown paragraph or bullet

    Args:
        tag: Paragraph tag

    Returns:
        Markdown paragraph or bullet list item
    """
    if has_bullet_marker(tag):
        for puce_img in tag.find_all("img", class_="spip_puce"):
            if isinstance(puce_img, Tag):
                puce_img.decompose()
        text: str = extract_inline_text(tag)
        return f"- {text.strip()}"
    return extract_inline_text(tag).strip()


def find_first_tag(parent: Tag, name: str, css_class: str = "") -> Optional[Tag]:
    """Find first child tag by name and optional CSS class

    Args:
        parent: Parent tag to search in
        name: Tag name to find
        css_class: Optional CSS class to filter by

    Returns:
        Found Tag or None
    """
    if css_class:
        result = parent.find(name, class_=css_class)
    else:
        result = parent.find(name)
    if isinstance(result, Tag):
        return result
    return None


def extract_image_block_parts(div_tag: Tag) -> tuple[str, str, str]:
    """Extract image, title, and description from a spip_documents div

    Args:
        div_tag: The spip_documents div tag

    Returns:
        Tuple of (markdown_image, title, description)
    """
    img_tag: Optional[Tag] = find_first_tag(div_tag, "img")
    markdown_image: str = ""
    if img_tag:
        alt: str = str(img_tag.get("alt", ""))
        src: str = str(img_tag.get("src", ""))
        markdown_image = f"![{alt}]({src})"

    title_div: Optional[Tag] = find_first_tag(
        div_tag, "div", "spip_doc_titre"
    )
    title: str = title_div.get_text(strip=True) if title_div else ""

    desc_div: Optional[Tag] = find_first_tag(
        div_tag, "div", "spip_doc_descriptif"
    )
    description: str = desc_div.get_text(strip=True) if desc_div else ""

    return markdown_image, title, description


def convert_image_block(tag: Tag) -> str:
    """Convert spip_documents div to Markdown image with caption

    Args:
        tag: The spip_documents div tag

    Returns:
        Markdown image with optional caption lines
    """
    markdown_image, title, description = extract_image_block_parts(tag)
    parts: list[str] = [markdown_image]
    if title:
        parts.append(f"_{title}_")
    if description:
        parts.append(f"_{description}_")
    return "\n".join(parts)


def extract_table_row(tr_tag: Tag) -> list[str]:
    """Extract cell text from a table row

    Args:
        tr_tag: Table row tag

    Returns:
        List of cell text strings
    """
    cells: list[str] = []
    for cell in tr_tag.find_all(["th", "td"]):
        cells.append(cell.get_text(strip=True))
    return cells


def convert_table(tag: Tag) -> str:
    """Convert table tag to Markdown table

    Args:
        tag: Table tag

    Returns:
        Markdown table string
    """
    rows: list[list[str]] = []
    header_row: Optional[list[str]] = None

    thead: Optional[Tag] = find_first_tag(tag, "thead")
    if thead:
        for tr in thead.find_all("tr"):
            header_row = extract_table_row(tr)

    for tr in tag.find_all("tr"):
        if thead and tr.find_parent("thead"):
            continue
        rows.append(extract_table_row(tr))

    if not header_row and rows:
        header_row = rows.pop(0)

    if not header_row:
        return ""

    col_count: int = len(header_row)
    header_line: str = "| " + " | ".join(header_row) + " |"
    separator_line: str = "| " + " | ".join(["---"] * col_count) + " |"
    data_lines: list[str] = []
    for row in rows:
        padded: list[str] = row + [""] * (col_count - len(row))
        data_lines.append("| " + " | ".join(padded[:col_count]) + " |")

    return "\n".join([header_line, separator_line] + data_lines)


def convert_element(
    element: Union[Tag, NavigableString, PageElement]
) -> Optional[str]:
    """Convert a single main content element to Markdown

    Args:
        element: HTML element to convert

    Returns:
        Markdown string or None to skip
    """
    if isinstance(element, NavigableString):
        text: str = str(element).strip()
        return text if text else None

    if not isinstance(element, Tag):
        return None

    if element.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
        return convert_heading(element)

    if element.name == "p":
        text = convert_paragraph(element)
        return text if text else None

    if element.name == "hr":
        return "---"

    if element.name == "div":
        css_class: Union[str, list[str]] = element.get("class", [])
        if "spip_documents" in css_class:
            return convert_image_block(element)

    if element.name == "table":
        return convert_table(element)

    return None


def convert_main_content(soup: BeautifulSoup) -> str:
    """Extract and convert main content div to Markdown

    Args:
        soup: Parsed BeautifulSoup object

    Returns:
        Markdown content string
    """
    result = soup.find("div", id="main")
    main_div: Optional[Tag] = result if isinstance(result, Tag) else None
    if not main_div:
        return ""

    blocks: list[str] = []
    for element in main_div.children:
        converted: Optional[str] = convert_element(element)
        if converted is not None:
            blocks.append(converted)

    return "\n\n".join(blocks)


def normalize_markdown(content: str) -> str:
    """Normalize whitespace in Markdown content

    Args:
        content: Raw Markdown string

    Returns:
        Normalized Markdown string
    """
    lines: list[str] = content.splitlines()
    normalized: list[str] = [line.rstrip() for line in lines]
    result: str = "\n".join(normalized)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def convert_html_to_markdown(html_content: str) -> str:
    """Convert HTML content string to Markdown

    Args:
        html_content: Raw HTML string

    Returns:
        Markdown string
    """
    soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
    content: str = convert_main_content(soup)
    return normalize_markdown(content)


def convert_html_file(input_file: str, output_dir: str) -> None:
    """Convert a single HTML file to Markdown

    Args:
        input_file: Path to input HTML file
        output_dir: Directory to save the Markdown file
    """
    with open(input_file, "r", encoding="utf-8") as f:
        html_content: str = f.read()

    markdown_content: str = convert_html_to_markdown(html_content)

    os.makedirs(output_dir, exist_ok=True)
    filename: str = os.path.basename(input_file)
    md_filename: str = filename.replace(".htm", ".md")
    output_file: str = os.path.join(output_dir, md_filename)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)


def convert_all_html_files(input_dir: str, output_dir: str) -> None:
    """Convert all HTML files in a directory to Markdown

    Args:
        input_dir: Directory containing HTML files
        output_dir: Directory to save Markdown files
    """
    html_files: list[str] = [
        f for f in os.listdir(input_dir) if f.endswith(".htm")
    ]

    for html_file in sorted(html_files):
        print(f"Converting {html_file}...")
        input_path: str = os.path.join(input_dir, html_file)
        convert_html_file(input_path, output_dir)

    print(f"Converted {len(html_files)} files to Markdown")


def main() -> None:
    """Main entry point"""
    input_dir: str = "assets/html"
    output_dir: str = "assets/md"

    print("Converting HTML files to Markdown...")
    convert_all_html_files(input_dir, output_dir)


if __name__ == "__main__":
    main()
