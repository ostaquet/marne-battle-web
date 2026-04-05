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
