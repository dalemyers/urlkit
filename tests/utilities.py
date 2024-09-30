"""Utilities for testing URL construction."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from urlkit.http.http_url import HttpUrl, QueryOptions


def assert_http_construction_expected_vs_components(expected: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""

    url = HttpUrl(**url_components)
    constructed = str(url)
    assert constructed == expected, f"Expected {expected}, got {constructed}"


def assert_http_parse_expected_vs_url(url: str, expected: dict) -> None:
    """Test that we can construct URLs correctly."""

    expected_constructed = HttpUrl(**expected)
    query_options = expected.get("query_options", QueryOptions())
    parsed = HttpUrl.parse(url, query_options)
    assert expected_constructed == parsed, f"Expected {expected}, got {expected_constructed}"
