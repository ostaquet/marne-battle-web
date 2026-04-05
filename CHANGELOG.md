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
