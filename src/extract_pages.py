import yaml
from datetime import datetime
from typing import Optional

from page import Page, PageType
from wayback_api import find_working_snapshot


def extract_all_working_versions() -> Optional[Page]:
    """Extract all working versions from archive.org

    Returns:
        Homepage Page with nested pages and articles, or None if not found
    """
    start_date: datetime = datetime(2010, 1, 1)
    end_date: datetime = datetime(2015, 12, 31)

    # Extract homepage
    homepage_url: str = "https://www.sambre-marne-yser.be/sommaire.php3"
    homepage_archive: Optional[str] = find_working_snapshot(
        homepage_url, start_date, end_date
    )

    if not homepage_archive:
        return None

    homepage: Page = Page(
        PageType.HOMEPAGE, homepage_url, homepage_archive
    )

    # Extract pages (01 to 99)
    for page_num in range(1, 100):
        page_url: str = (
            f"https://www.sambre-marne-yser.be/page_{page_num:02d}.php3"
        )

        page_archive: Optional[str] = find_working_snapshot(
            page_url, start_date, end_date
        )

        if page_archive:
            page: Page = Page(PageType.PAGE, page_url, page_archive)
            homepage.add_child(page)

    return homepage


def save_to_yaml(page: Page, output_file: str) -> None:
    """Save page data to a YAML file

    Args:
        page: Page to save
        output_file: Path to output YAML file
    """
    data: dict[str, object] = page.to_dict()

    with open(output_file, "w", encoding="utf-8") as file:
        yaml.dump(data, file, default_flow_style=False, allow_unicode=True)


def main() -> None:
    """Main entry point"""
    print("Extracting pages from Internet Archive...")

    homepage: Optional[Page] = extract_all_working_versions()

    if not homepage:
        print("Error: Could not find homepage in archive")
        return

    output_file: str = "assets/pages.yaml"
    save_to_yaml(homepage, output_file)

    print(f"Pages saved to {output_file}")


if __name__ == "__main__":
    main()
