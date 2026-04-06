"""Relink HTML files to use local references"""

import os
import re
import yaml
from typing import Optional
from bs4 import BeautifulSoup


def extract_page_number(url: str) -> str:
    """Extract page number from URL

    Args:
        url: URL containing page_XX.php3

    Returns:
        Page number as zero-padded string, or empty string if not found
    """
    match: Optional[re.Match[str]] = re.search(r'page_(\d+)\.php3', url)
    if match:
        return match.group(1).zfill(2)
    return ""


def extract_article_numbers(url: str) -> tuple[str, str]:
    """Extract page and article numbers from URL

    Args:
        url: URL containing article=X.php3?id_article=Y

    Returns:
        Tuple of (page_number, article_number) as zero-padded strings
    """
    match: Optional[re.Match[str]] = re.search(
        r'article=(\d+)\.php3\?id_article=(\d+)', url
    )
    if match:
        page_num: str = match.group(1).zfill(2)
        article_num: str = match.group(2).zfill(2)
        return page_num, article_num
    return "", ""


def relink_page_href(href: str) -> str:
    """Relink a page href to local version

    Args:
        href: Original href attribute

    Returns:
        New href for local file, or empty string if cannot relink
    """
    # Homepage
    if "sommaire.php3" in href:
        return "homepage.htm"

    # Archive URL ending with root
    if href.endswith("://www.sambre-marne-yser.be/"):
        return "homepage.htm"

    # Page
    page_num: str = extract_page_number(href)
    if page_num:
        return f"page_{page_num}.htm"

    # Article
    page_num, article_num = extract_article_numbers(href)
    if page_num and article_num:
        return f"article_{page_num}_{article_num}.htm"

    # Cannot relink (external link or unknown format)
    return ""


def relink_img_src(src: str, img_map: dict[str, str]) -> str:
    """Relink an image src to local version

    Args:
        src: Original src attribute
        img_map: Mapping of archive URLs to local filenames

    Returns:
        New src for local file, or empty string if not found in map
    """
    if src in img_map:
        return f"../img/{img_map[src]}"
    return ""


def relink_html_file(
    input_file: str,
    output_dir: str,
    img_map: dict[str, str],
    log_file: str
) -> None:
    """Relink HTML file to use local references

    Args:
        input_file: Path to input HTML file
        output_dir: Directory to save relinked HTML
        img_map: Mapping of archive URLs to local filenames
        log_file: Path to log file for unmatched links
    """
    # Read HTML
    with open(input_file, "r", encoding="utf-8") as f:
        html_content: str = f.read()

    soup = BeautifulSoup(html_content, "html.parser")
    filename: str = os.path.basename(input_file)

    # Track unmatched links for logging
    unmatched: list[str] = []

    # Relink all <a> tags
    for a_tag in soup.find_all("a"):
        href: Optional[str] = a_tag.get("href")
        if href:
            new_href: str = relink_page_href(href)
            if new_href:
                a_tag["href"] = new_href
            else:
                # Log unmatched link (unless it's just a fragment)
                if not href.startswith("#"):
                    unmatched.append(f"{filename} : {href}")

    # Relink all <img> tags
    for img_tag in soup.find_all("img"):
        src: Optional[str] = img_tag.get("src")
        if src:
            new_src: str = relink_img_src(src, img_map)
            if new_src:
                img_tag["src"] = new_src
            else:
                # Log unmatched image
                unmatched.append(f"{filename} : {src}")

    # Save relinked HTML
    os.makedirs(output_dir, exist_ok=True)
    output_file: str = os.path.join(output_dir, filename)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(str(soup))

    # Append to log file if there are unmatched links
    if unmatched:
        with open(log_file, "a", encoding="utf-8") as f:
            for line in unmatched:
                f.write(line + "\n")


def process_all_html_files(
    input_dir: str,
    output_dir: str,
    img_map_file: str,
    log_file: str
) -> None:
    """Process all HTML files and relink them

    Args:
        input_dir: Directory containing raw HTML files
        output_dir: Directory to save relinked HTML files
        img_map_file: Path to image mapping YAML file
        log_file: Path to log file for unmatched links
    """
    # Load image map
    img_map: dict[str, str] = {}
    if os.path.exists(img_map_file):
        with open(img_map_file, "r", encoding="utf-8") as f:
            img_map = yaml.safe_load(f) or {}
        print(f"Loaded {len(img_map)} image mappings")

    # Clear log file
    if os.path.exists(log_file):
        os.remove(log_file)

    # Process each HTML file
    html_files: list[str] = [
        f for f in os.listdir(input_dir) if f.endswith(".htm")
    ]

    for html_file in sorted(html_files):
        print(f"Processing {html_file}...")
        input_path: str = os.path.join(input_dir, html_file)
        relink_html_file(input_path, output_dir, img_map, log_file)

    print(f"Relinked {len(html_files)} files")
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            unmatched_count: int = len(f.readlines())
        print(f"Unmatched links logged: {unmatched_count}")


def main() -> None:
    """Main entry point"""
    input_dir: str = "assets/raw_html"
    output_dir: str = "assets/html"
    img_map_file: str = "assets/img_map.yaml"
    log_file: str = "assets/relink.log"

    print("Relinking HTML files...")
    process_all_html_files(input_dir, output_dir, img_map_file, log_file)


if __name__ == "__main__":
    main()
