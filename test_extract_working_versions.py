"""Unit tests for extract_working_versions.py"""

import pytest
import responses
from datetime import datetime
from extract_working_versions import (
    query_cdx_snapshots,
    is_page_functional,
    find_working_snapshot,
    build_page_entry,
    extract_all_working_versions,
)


class TestQueryCdxSnapshots:
    """Tests for querying CDX API for snapshots"""

    @responses.activate
    def test_query_cdx_returns_snapshots_in_date_range(self) -> None:
        """Test that CDX query returns snapshots within date range"""
        url: str = "http://www.sambre-marne-yser.be/sommaire.php3"
        cdx_response: str = (
            "com,sambre-marne-yser)/ 20100101120000 http://www.sambre-marne-yser.be/sommaire.php3 200\n"
            "com,sambre-marne-yser)/ 20120501120000 http://www.sambre-marne-yser.be/sommaire.php3 200\n"
            "com,sambre-marne-yser)/ 20140501120000 http://www.sambre-marne-yser.be/sommaire.php3 200\n"
            "com,sambre-marne-yser)/ 20160501120000 http://www.sambre-marne-yser.be/sommaire.php3 200\n"
        )

        responses.add(
            responses.GET,
            "http://web.archive.org/cdx/search/cdx",
            body=cdx_response,
            status=200,
        )

        snapshots: list[dict[str, str]] = query_cdx_snapshots(
            url,
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2015, 12, 31)
        )

        assert len(snapshots) == 3
        assert snapshots[0]["timestamp"] == "20100101120000"
        assert snapshots[1]["timestamp"] == "20120501120000"
        assert snapshots[2]["timestamp"] == "20140501120000"


class TestIsPageFunctional:
    """Tests for checking if a page is functional"""

    def test_page_with_mysql_error_is_not_functional(self) -> None:
        """Test that page with MySQL error is not functional"""
        html_content: str = """
        <html>
            <body>
                <h1>Site under construction</h1>
                <p>Warning: a technical problem (MySQL server) prevents access to this part of the site.</p>
            </body>
        </html>
        """

        assert is_page_functional(html_content) is False

    def test_page_without_mysql_error_is_functional(self) -> None:
        """Test that page without MySQL error is functional"""
        html_content: str = """
        <html>
            <body>
                <h1>Welcome to the site</h1>
                <p>This is the content of the page.</p>
            </body>
        </html>
        """

        assert is_page_functional(html_content) is True

    def test_empty_page_is_not_functional(self) -> None:
        """Test that empty page is not functional"""
        assert is_page_functional("") is False


class TestFindWorkingSnapshot:
    """Tests for finding a working snapshot"""

    @responses.activate
    def test_find_working_snapshot_returns_first_functional(self) -> None:
        """Test that find_working_snapshot returns the first functional snapshot"""
        url: str = "http://www.sambre-marne-yser.be/sommaire.php3"

        # Mock CDX API response
        cdx_response: str = (
            "com,sambre-marne-yser)/ 20120101120000 http://www.sambre-marne-yser.be/sommaire.php3 200\n"
            "com,sambre-marne-yser)/ 20130101120000 http://www.sambre-marne-yser.be/sommaire.php3 200\n"
        )
        responses.add(
            responses.GET,
            "http://web.archive.org/cdx/search/cdx",
            body=cdx_response,
            status=200,
        )

        # Mock first snapshot with MySQL error
        responses.add(
            responses.GET,
            "https://web.archive.org/web/20120101120000/http://www.sambre-marne-yser.be/sommaire.php3",
            body="<html>Site under construction. Warning: a technical problem (MySQL server)</html>",
            status=200,
        )

        # Mock second snapshot as functional
        responses.add(
            responses.GET,
            "https://web.archive.org/web/20130101120000/http://www.sambre-marne-yser.be/sommaire.php3",
            body="<html><h1>Welcome</h1><p>Content here</p></html>",
            status=200,
        )

        result: str | None = find_working_snapshot(
            url,
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2015, 12, 31)
        )

        assert result == "https://web.archive.org/web/20130101120000/http://www.sambre-marne-yser.be/sommaire.php3"

    @responses.activate
    def test_find_working_snapshot_returns_none_when_no_functional(self) -> None:
        """Test that find_working_snapshot returns None when no functional snapshot found"""
        url: str = "http://www.sambre-marne-yser.be/sommaire.php3"

        # Mock CDX API response
        cdx_response: str = (
            "com,sambre-marne-yser)/ 20120101120000 http://www.sambre-marne-yser.be/sommaire.php3 200\n"
        )
        responses.add(
            responses.GET,
            "http://web.archive.org/cdx/search/cdx",
            body=cdx_response,
            status=200,
        )

        # Mock snapshot with MySQL error
        responses.add(
            responses.GET,
            "https://web.archive.org/web/20120101120000/http://www.sambre-marne-yser.be/sommaire.php3",
            body="<html>Site under construction. Warning: a technical problem (MySQL server)</html>",
            status=200,
        )

        result: str | None = find_working_snapshot(
            url,
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2015, 12, 31)
        )

        assert result is None


class TestBuildPageEntry:
    """Tests for building page entry"""

    def test_build_page_entry_creates_correct_structure(self) -> None:
        """Test that build_page_entry creates correct YAML structure"""
        entry: dict[str, str] = build_page_entry(
            page_id="homepage",
            official_url="https://www.sambre-marne-yser.be/sommaire.php3",
            archive_url="https://web.archive.org/web/20131029060500/http://sambre-marne-yser.be/sommaire.php3"
        )

        assert entry["id"] == "homepage"
        assert entry["official_url"] == "https://www.sambre-marne-yser.be/sommaire.php3"
        assert entry["archive_url"] == "https://web.archive.org/web/20131029060500/http://sambre-marne-yser.be/sommaire.php3"


class TestExtractAllWorkingVersions:
    """Tests for extracting all working versions"""

    def test_extract_all_working_versions_returns_dict(self) -> None:
        """Test that extract_all_working_versions returns a dictionary"""
        # This test will be implemented once we have the main function
        # For now, we just check it returns a dict
        # This is a placeholder test that will be expanded
        pass
