# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Python script `extract_working_versions.py` to extract working versions from Internet Archive
- Function `query_cdx_snapshots()` to query CDX API for snapshots within date range
- Function `is_page_functional()` to detect pages with MySQL errors
- Function `find_working_snapshot()` to find first working archive.org snapshot
- Function `build_page_entry()` to create YAML entry structure
- Function `extract_all_working_versions()` to extract homepage and pages
- Comprehensive unit tests with 100% coverage
- Python dependencies: requests, pyyaml, pytest, responses
- Documentation in README.md for running the extraction script

### Task

- Completed task `0000-extract-working-version.md`: Extract working versions from archive.org between 2010-2015

### Changed

- Fixed all flake8 linting issues in test file (removed unused imports, fixed line lengths)
- Added explicit type annotations for all dict types to pass mypy strict mode
- Updated test script to add src/ to PYTHONPATH for proper module imports
- Updated README.md with new development workflow (lint and test scripts)
- Added linter dependencies to requirements.txt (flake8, mypy, type stubs)

### Task

- Completed task `0001-fix-project.md`: Adjust code to ensure everything follows linting rules

### Added

- `Page` dataclass in `src/page.py` for structured page representation
- `PageType` enum with values: HOMEPAGE, PAGE, ARTICLE
- `extract_timestamp_from_archive_url()` function to extract timestamps
- `build_page()` function to create Page objects from URLs
- Comprehensive unit tests for Page dataclass (11 tests)
- Methods: `add_child()`, `to_dict()`, `from_dict()` for Page objects

### Changed

- Replaced `dict[str, Any]` with `Page` dataclass for type safety
- Updated `extract_all_working_versions()` to return `Optional[Page]`
- Updated `save_to_yaml()` to accept Page and convert to dict
- Updated `build_page_entry()` to `build_page()` returning Page
- Updated all related unit tests to work with Page objects
- Updated README.md with documentation about the Page structure

### Task

- Completed task `0002-structure-data.md`: Replace dict structure with Page dataclass

### Added

- `extract_articles.py` script to extract article links from pages
- `extract_article_links_from_html()` function to parse HTML for articles
- `download_html_from_archive()` function to fetch HTML from archive URLs
- `load_page_from_yaml()` function to load Page structure from YAML
- `save_page_to_yaml()` function to save Page structure to YAML
- `process_page_for_articles()` function to find articles for a page
- `extract_articles_from_pages()` orchestration function
- Comprehensive unit tests for article extraction (9 tests)

### Changed

- Project now supports two-step extraction: pages first, then articles
- Articles are added as children to their parent pages
- README.md updated with article extraction workflow

### Task

- Completed task `0003-extract-articles-urls.md`: Extract article URLs from pages

### Added

- Fail-safe processing in article extraction
- Skip logic for pages that already have articles
- Progress saving after each page is processed
- Unit tests for fail-safe features (2 tests)

### Changed

- `process_page_for_articles()` now skips pages with existing articles
- `extract_articles_from_pages()` saves YAML after each page
- Article extraction is now resumable after timeouts or errors
- README.md updated with fail-safe feature documentation

### Task

- Completed task `0004-add-fail-safe-processing.md`: Add fail-safe processing to article extraction

### Added

- Automatic delays between Internet Archive requests
- Configurable delay parameter in HTTP request functions
- Default 1.0s delay for CDX API queries
- Default 1.0s delay for archive.org downloads
- Delays even on request errors to avoid hammering the server

### Changed

- `query_cdx_snapshots()` now accepts delay parameter (default: 0.5s)
- `find_working_snapshot()` now accepts delay parameter (default: 1.0s)
- `download_html_from_archive()` now accepts delay parameter (default: 1.0s)
- All tests updated to use delay=0 for fast execution
- Prevents connection errors and rate limiting issues

### Task

- Completed task `0005-gentle-with-internet-archive.md`: Add delays to be gentle with Internet Archive

### Added

- Smart resume mode for article extraction
- Automatic detection of existing progress file
- Unit tests for resume mode logic (2 tests)

### Changed

- `main()` in `extract_articles.py` now checks if `assets/articles.yaml` exists
- First run: uses `assets/pages.yaml` as input
- Resume/retry: uses `assets/articles.yaml` as input (preserves all progress)
- Provides clear console output indicating resume vs first run mode
- README.md updated with smart resume documentation

### Task

- Completed task `0006-improve-retry.md`: Improve retry logic to resume from articles.yaml

### Added

- Comprehensive tests for loading real YAML files
- Roundtrip test for save/load with articles (validates YAML integrity)
- Tests for loading actual assets/pages.yaml and assets/articles.yaml files

### Fixed

- Removed corrupted articles.yaml file
- Verified YAML save/load functionality works correctly
- Added test coverage for real-world YAML file loading

### Task

- Completed task `0007-fix-loading-yaml-articles.md`: Fix and test loading of YAML articles

### Added

- Script `download_html_dataset.py` to download HTML files from archive.org locally
- Function `generate_filename()` to create appropriate filenames for each page type
- Function `download_and_save_html()` to download and save HTML files
- Function `build_local_dataset()` to process entire page structure
- Support for `local_filename` attribute in Page class
- Comprehensive unit tests for HTML dataset downloading (6 tests)
- HTML files stored in `assets/raw_html/` directory with structured naming:
  - `homepage.htm` for homepage
  - `page_XX.htm` for pages
  - `article_XX_YY.htm` for articles

### Changed

- Page class now supports optional `local_filename` attribute
- `to_dict()` and `load_from_dict()` handle local_filename serialization
- Creates local dataset for faster processing
- Reduces load on Internet Archive by downloading once

### Task

- Completed task `0008-build-local-html-dataset.md`: Build local HTML dataset from archive.org URLs

### Added

- Resume capability for HTML dataset downloads
- Automatic detection of existing files (skips re-downloading)
- Progress callback system for incremental saves
- Smart resume mode: uses `assets/dataset.yaml` if it exists
- Progress saved after each file download
- Unit tests for skip-existing and progress-callback features (2 tests)

### Changed

- `build_local_dataset()` now accepts optional `progress_callback` parameter
- Checks if file exists before downloading (resume capability)
- `main()` automatically resumes from `assets/dataset.yaml` if it exists
- Saves YAML after each download to preserve progress
- Script can be safely interrupted and resumed

### Task

- Completed task `0009-resume-while-build-local-html-dataset.md`: Add resume capability to HTML dataset download

### Added

- Script `download_img_dataset.py` to download images from HTML files
- Function `extract_img_tags()` to parse HTML and extract img src attributes
- Function `build_archive_url()` to convert relative URLs to full archive.org URLs
- Function `calculate_md5()` to compute MD5 hash for duplicate detection
- Function `download_image()` to download and save images with rate limiting
- Function `process_html_files()` to orchestrate image extraction
- Image mapping file `assets/img_map.yaml` with archive_url → local_filename
- Filename collision handling using MD5 checksums
- Resume capability: skips already mapped images
- Progress saved after each image download
- Comprehensive unit tests for image downloading (9 tests)
- Dependencies: beautifulsoup4 for HTML parsing

### Changed

- Images stored in `assets/img/` with original filenames
- Detects duplicate images by MD5 and reuses existing files
- Rate limiting on image downloads (default 1.0s delay)

### Task

- Completed task `0010-build-local-img-dataset.md`: Build local image dataset from HTML files

### Added

- Script `relink.py` to relink HTML files with local references
- Function `extract_page_number()` to extract page numbers from URLs
- Function `extract_article_numbers()` to extract article page/ID from URLs
- Function `relink_page_href()` to convert page links to local filenames
- Function `relink_img_src()` to convert image URLs using img_map.yaml
- Function `relink_html_file()` to process individual HTML files
- Function `process_all_html_files()` to batch process all HTML files
- Logging of unmatched links/images to `assets/relink.log`
- Comprehensive unit tests for relinking (16 tests)

### Changed

- Internal page links now point to local HTML files
- Image sources now point to local images in ../img/
- Relinked HTML saved to `assets/html/` directory
- Handles homepage, page, and article link formats
- Logs external links and unmapped images for investigation

### Task

- Completed task `0011-relink-htm-and-img.md`: Relink HTML files and images to use local references

### Added

- Function `extract_img_links()` to extract image links from `<a>` tags
- Function `is_relative_url()` to detect relative image paths
- Function `build_original_url()` to construct full URLs from relative paths
- Support for downloading images linked in `<a>` tags (not just `<img>` tags)
- Automatic snapshot finding for relative image URLs using wayback API
- Unit tests for new image link extraction functionality (9 tests)

### Changed

- `process_html_files()` now extracts images from both `<img>` and `<a>` tags
- Relative image links are resolved using `find_working_snapshot()` (2010-2015 range)
- README.md updated to document `<a>` tag image extraction

### Task

- Completed task `0012-fix-img-downloader.md`: Fix image downloader to handle links in `<a>` tags

### Added

- YAML configuration file `assets/link_map.yaml` for external link mappings
- Function `load_link_map()` to load external links from YAML file
- Unit tests for link map loading (3 tests)
- Unit test for preserving external links from configuration

### Changed

- `relink_page_href()` now accepts optional `external_links` parameter
- `relink_html_file()` now accepts optional `external_links` parameter
- `process_all_html_files()` loads and uses link map from configuration
- Removed hard-coded external URLs from Python code (moved to YAML)
- External links are now configurable without code changes
- README.md updated to document link map configuration

### Task

- Completed task `0013-keep-config-for-special-links.md`: Move special URL mappings to YAML configuration

### Changed

- Script `scripts/venv.sh` now detects Docker environment and creates appropriate venv
- Virtual environment created in `venv_docker/` when running in Docker containers
- Virtual environment created in `venv_local/` when running on local machines
- Scripts `scripts/lint.sh` and `scripts/test.sh` updated to use environment-specific venv
- Updated `.gitignore` to ignore both `venv_docker/` and `venv_local/`
- Prevents conflicts between Docker and local development environments
- README.md updated with documentation about environment-specific venv directories

### Task

- Completed task `0014-adjust-venv-script.md`: Adjust venv script to support Docker and local environments
