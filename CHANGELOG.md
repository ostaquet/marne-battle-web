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
