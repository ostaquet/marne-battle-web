"""Download images from HTML files and build image mapping"""

import os
import re
import hashlib
import yaml
from typing import Optional
from bs4 import BeautifulSoup

from delay import wait_for
from wayback_api import download_and_save_binary


def extract_img_tags(html_content: str) -> list[str]:
    """Extract all img src attributes from HTML

    Args:
        html_content: HTML content to parse

    Returns:
        List of img src URLs
    """
    soup = BeautifulSoup(html_content, "html.parser")
    img_tags = soup.find_all("img")

    img_srcs: list[str] = []
    for img in img_tags:
        src: Optional[str] = img.get("src")
        if src:
            img_srcs.append(src)

    return img_srcs


def build_archive_url(relative_url: str) -> str:
    """Build full archive.org URL from relative path

    Args:
        relative_url: Relative or absolute URL

    Returns:
        Full archive.org URL
    """
    if relative_url.startswith("http"):
        return relative_url

    # Add https://web.archive.org prefix
    if relative_url.startswith("/"):
        return f"https://web.archive.org{relative_url}"

    return f"https://web.archive.org/{relative_url}"


def calculate_md5(file_path: str) -> str:
    """Calculate MD5 hash of a file

    Args:
        file_path: Path to the file

    Returns:
        MD5 hash as hex string
    """
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def process_html_files(
    html_dir: str,
    img_dir: str,
    output_yaml: str,
    delay_between_calls: int = 10
) -> None:
    """Process all HTML files and download images

    Args:
        html_dir: Directory containing HTML files
        img_dir: Directory to save images
        output_yaml: Path to output YAML mapping file
        delay: Seconds to wait between downloads (default: 1.0)
    """
    # Image mapping: archive_url -> local_filename
    img_map: dict[str, str] = {}

    # Load existing mapping if it exists (resume capability)
    if os.path.exists(output_yaml):
        with open(output_yaml, "r", encoding="utf-8") as f:
            img_map = yaml.safe_load(f) or {}
        print(f"Resuming from {output_yaml} ({len(img_map)} images already mapped)")

    # Process each HTML file
    html_files: list[str] = [
        f for f in os.listdir(html_dir) if f.endswith(".htm")
    ]

    for html_file in sorted(html_files):
        print(f"Processing {html_file}...")
        html_path: str = os.path.join(html_dir, html_file)

        with open(html_path, "r", encoding="utf-8") as f:
            html_content: str = f.read()

        # Extract image URLs
        img_srcs: list[str] = extract_img_tags(html_content)

        for img_src in img_srcs:
            # Skip if already processed
            if img_src in img_map:
                print(f"  Skipping {img_src} (already mapped)")
                continue

            # Build full URL
            archive_url: str = build_archive_url(img_src)

            # Extract filename
            match: Optional[re.Match[str]] = re.search(
                r'/([^/]+\.(jpg|jpeg|png|gif|bmp|svg))$',
                img_src,
                re.IGNORECASE
            )
            if not match:
                print(f"  Skipping {img_src} (cannot extract filename)")
                continue

            filename: str = match.group(1)
            output_path: str = os.path.join(img_dir, filename)

            # Handle filename collision
            if os.path.exists(output_path):
                # Download to temp file to check MD5
                temp_path: str = os.path.join(img_dir, f"temp_{filename}")
                success: bool = download_and_save_binary(
                    archive_url, img_dir, f"temp_{filename}"
                )

                if success:
                    # Check if content is the same
                    existing_md5: str = calculate_md5(output_path)
                    new_md5: str = calculate_md5(temp_path)

                    if existing_md5 == new_md5:
                        print(f"  {filename} - same content, reusing existing file")
                        os.remove(temp_path)
                    else:
                        print(f"  {filename} - different content, keeping new file")
                        os.remove(temp_path)
                        # For now, just use the existing file
                        # In a more complex scenario, we'd rename the new file

                    # Map to existing file
                    img_map[img_src] = filename
                else:
                    print(f"  Failed to download {img_src}")
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            else:
                # Download the image
                print(f"  Downloading {filename}...")
                success = download_and_save_binary(archive_url, img_dir, filename)

                if success:
                    img_map[img_src] = filename
                    print(f"    Saved as {filename}")
                else:
                    print("    Failed to download")

            # Save progress after each image
            with open(output_yaml, "w", encoding="utf-8") as f:
                yaml.dump(img_map, f, default_flow_style=False, allow_unicode=True)

            wait_for(delay_between_calls)

    print(f"Image mapping saved to {output_yaml}")
    print(f"Total images: {len(img_map)}")


def main() -> None:
    """Main entry point"""
    html_dir: str = "assets/raw_html"
    img_dir: str = "assets/img"
    output_yaml: str = "assets/img_map.yaml"

    print(f"Processing HTML files from {html_dir}...")
    process_html_files(html_dir, img_dir, output_yaml)


if __name__ == "__main__":
    main()
