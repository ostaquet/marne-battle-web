from datetime import datetime

import responses

from wayback_api import (
    _is_page_functional,
    _query_all_available_snapshots,
    find_working_snapshot
)


class TestQueryCdxSnapshots:
    """Tests for querying CDX API for snapshots"""

    @responses.activate
    def test_query_cdx_returns_snapshots_in_date_range(self) -> None:
        """Test that CDX query returns snapshots within date range"""
        url: str = "http://www.sambre-marne-yser.be/sommaire.php3"
        cdx_response: str = (
            "com,sambre-marne-yser)/ 20100101120000 "
            "http://www.sambre-marne-yser.be/sommaire.php3 200\n"
            "com,sambre-marne-yser)/ 20120501120000 "
            "http://www.sambre-marne-yser.be/sommaire.php3 200\n"
            "com,sambre-marne-yser)/ 20140501120000 "
            "http://www.sambre-marne-yser.be/sommaire.php3 200\n"
            "com,sambre-marne-yser)/ 20160501120000 "
            "http://www.sambre-marne-yser.be/sommaire.php3 200\n"
        )

        responses.add(
            responses.GET,
            "https://web.archive.org/cdx/search/cdx",
            body=cdx_response,
            status=200,
        )

        snapshots: list[dict[str, str]] = _query_all_available_snapshots(
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
                <p>Warning: a technical problem (MySQL server)
                prevents access to this part of the site.</p>
            </body>
        </html>
        """

        assert _is_page_functional(html_content) is False

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

        assert _is_page_functional(html_content) is True

    def test_empty_page_is_not_functional(self) -> None:
        """Test that empty page is not functional"""
        assert _is_page_functional("") is False


class TestFindWorkingSnapshot:
    """Tests for finding a working snapshot"""

    @responses.activate
    def test_find_working_snapshot_returns_first_functional(self) -> None:
        """Test find_working_snapshot returns first functional snapshot"""
        url: str = "http://www.sambre-marne-yser.be/sommaire.php3"

        # Mock CDX API response
        cdx_response: str = (
            "com,sambre-marne-yser)/ 20120101120000 "
            "http://www.sambre-marne-yser.be/sommaire.php3 200\n"
            "com,sambre-marne-yser)/ 20130101120000 "
            "http://www.sambre-marne-yser.be/sommaire.php3 200\n"
        )
        responses.add(
            responses.GET,
            "https://web.archive.org/cdx/search/cdx",
            body=cdx_response,
            status=200,
        )

        # Mock first snapshot with MySQL error
        snapshot_url_1: str = (
            "https://web.archive.org/web/20120101120000/"
            "http://www.sambre-marne-yser.be/sommaire.php3"
        )
        responses.add(
            responses.GET,
            snapshot_url_1,
            body=(
                "<html>Site under construction. "
                "Warning: a technical problem (MySQL server)</html>"
            ),
            status=200,
        )

        # Mock second snapshot as functional
        snapshot_url_2: str = (
            "https://web.archive.org/web/20130101120000/"
            "http://www.sambre-marne-yser.be/sommaire.php3"
        )
        responses.add(
            responses.GET,
            snapshot_url_2,
            body="<html><h1>Welcome</h1><p>Content here</p></html>",
            status=200,
        )

        result: str | None = find_working_snapshot(
            url,
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2015, 12, 31),
            delay_in_seconds=0
        )

        expected_url: str = (
            "https://web.archive.org/web/20130101120000/"
            "http://www.sambre-marne-yser.be/sommaire.php3"
        )
        assert result == expected_url

    @responses.activate
    def test_find_working_snapshot_returns_none_when_no_functional(
        self
    ) -> None:
        """Test find_working_snapshot returns None when no functional"""
        url: str = "http://www.sambre-marne-yser.be/sommaire.php3"

        # Mock CDX API response
        cdx_response: str = (
            "com,sambre-marne-yser)/ 20120101120000 "
            "http://www.sambre-marne-yser.be/sommaire.php3 200\n"
        )
        responses.add(
            responses.GET,
            "https://web.archive.org/cdx/search/cdx",
            body=cdx_response,
            status=200,
        )

        # Mock snapshot with MySQL error
        snapshot_url: str = (
            "https://web.archive.org/web/20120101120000/"
            "http://www.sambre-marne-yser.be/sommaire.php3"
        )
        responses.add(
            responses.GET,
            snapshot_url,
            body=(
                "<html>Site under construction. "
                "Warning: a technical problem (MySQL server)</html>"
            ),
            status=200,
        )

        result: str | None = find_working_snapshot(
            url,
            start_date=datetime(2010, 1, 1),
            end_date=datetime(2015, 12, 31),
            delay_in_seconds=0
        )

        assert result is None
