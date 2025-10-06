"""Test the construction or URLs."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from urlkit.http.http_url import _parse_http_or_https_url

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
    assert _parse_http_or_https_url(url).netloc == expected


@pytest.mark.parametrize(
    "url,expected",
    [
        ("http:a/path/here", None),
        ("http:/a/path/here", None),
    ],
)
def test_relative(url: str, expected: str) -> None:
    """Test that we can construct URLs correctly."""
    assert _parse_http_or_https_url(url).netloc == expected


def test_parse_ipv6_missing_closing_bracket() -> None:
    """Test parsing IPv6 address without closing bracket."""
    from urlkit.http import HttpUrl

    with pytest.raises(ValueError) as exc_info:
        HttpUrl.parse("http://[::1/")

    assert "Invalid IPv6 address, missing closing ']'" in str(exc_info.value)


def test_parse_ipv6_with_empty_port() -> None:
    """Test parsing IPv6 address with colon but empty port."""
    from urlkit.http import HttpUrl

    # IPv6 with trailing colon but no port number
    url = HttpUrl.parse("http://[::1]:/path")
    assert url.host == "[::1]"
    assert url.port is None
    assert str(url.path) == "/path"


def test_parse_ipv6_unexpected_characters_after_bracket() -> None:
    """Test parsing IPv6 with invalid characters after bracket."""
    from urlkit.http import HttpUrl

    with pytest.raises(ValueError) as exc_info:
        HttpUrl.parse("http://[::1]abc/path")

    assert "Invalid IPv6 address, unexpected characters after ']'" in str(exc_info.value)
