"""Test the construction or URLs."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from urlkit.http.http_url import parse_http_or_https_url

# pylint: enable=wrong-import-position


@pytest.mark.parametrize(
    "url,expected",
    [
        ("http://example.com", "example.com"),
        ("http://example.com/some/path", "example.com"),
        ("http://example.com:8080/home", "example.com:8080"),
        ("http://username@example.com/", "username@example.com"),
        ("http://username:password@example.com:1234", "username:password@example.com:1234"),
    ],
)
def test_netloc(url: str, expected: str) -> None:
    """Test that we can construct URLs correctly."""
    assert parse_http_or_https_url(url).netloc == expected


@pytest.mark.parametrize(
    "url,expected",
    [
        ("http:a/path/here", None),
        ("http:/a/path/here", None),
    ],
)
def test_relative(url: str, expected: str) -> None:
    """Test that we can construct URLs correctly."""
    assert parse_http_or_https_url(url).netloc == expected
