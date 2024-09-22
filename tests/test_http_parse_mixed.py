"""Test the construction or URLs."""

import os
import sys

import pytest

from utilities import assert_http_parse_expected_vs_url

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from urlkit.http_url import HttpUrl, HttpsUrl, parse_http_or_https_url, QueryOptions

# pylint: enable=wrong-import-position


@pytest.mark.parametrize(
    "url,url_components",
    [
        (
            "http://http://http://@http://http://?http://#http://",
            {
                "scheme": "http",
                "username": "http",
                "password": "//http://",
                "host": "http",
                "path": "//http://",
                "query": "http://",
                "fragment": "http://",
            },
        ),
        (
            "http://example.com",
            {
                "scheme": "http",
                "host": "example.com",
            },
        ),
        (
            "http://example.com:80",
            {"scheme": "http", "host": "example.com", "port": 80},
        ),
        (
            "http://example.com/foo",
            {"scheme": "http", "host": "example.com", "path": "/foo"},
        ),
        (
            "https://example.com?foo=bar",
            {
                "scheme": "https",
                "host": "example.com",
                "query": {"foo": "bar"},
            },
        ),
        (
            "https://example.com?foo=bar#fragment",
            {
                "scheme": "https",
                "host": "example.com",
                "query": {"foo": "bar"},
                "fragment": "fragment",
            },
        ),
        (
            "https://example.com/path?foo=bar#fragment",
            {
                "scheme": "https",
                "host": "example.com",
                "path": "/path",
                "query": {"foo": "bar"},
                "fragment": "fragment",
            },
        ),
        (
            "https://username@example.com/path?foo=bar#fragment",
            {
                "scheme": "https",
                "username": "username",
                "host": "example.com",
                "path": "/path",
                "query": {"foo": "bar"},
                "fragment": "fragment",
            },
        ),
        (
            "https://username:password@example.com/path?foo=bar#fragment",
            {
                "scheme": "https",
                "username": "username",
                "password": "password",
                "host": "example.com",
                "path": "/path",
                "query": {"foo": "bar"},
                "fragment": "fragment",
            },
        ),
        (
            "https://username:password@example.com/path:with:colons?foo=bar#fragment",
            {
                "scheme": "https",
                "username": "username",
                "password": "password",
                "host": "example.com",
                "path": "/path:with:colons",
                "query": {"foo": "bar"},
                "fragment": "fragment",
            },
        ),
        (
            "https://username:password@example.com/path:with:colons@and@at?foo=bar#fragment",
            {
                "scheme": "https",
                "username": "username",
                "password": "password",
                "host": "example.com",
                "path": "/path:with:colons@and@at",
                "query": {"foo": "bar"},
                "fragment": "fragment",
            },
        ),
        (
            "https://username:password:with:colons@example.com/path?foo=bar#fragment",
            {
                "scheme": "https",
                "username": "username",
                "password": "password:with:colons",
                "host": "example.com",
                "path": "/path",
                "query": {"foo": "bar"},
                "fragment": "fragment",
            },
        ),
        (
            "https://username:password@example.com:/path?foo=bar#fragment",
            {
                "scheme": "https",
                "username": "username",
                "password": "password",
                "host": "example.com",
                "path": "/path",
                "query": {"foo": "bar"},
                "fragment": "fragment",
            },
        ),
        (
            "https://username:password@example.com:88/path?foo=bar#fragment",
            {
                "scheme": "https",
                "username": "username",
                "password": "password",
                "host": "example.com",
                "port": 88,
                "path": "/path",
                "query": {"foo": "bar"},
                "fragment": "fragment",
            },
        ),
        (
            "https://username:password@example.com:88/path@newexample.net?foo=bar#fragment",
            {
                "scheme": "https",
                "username": "username",
                "password": "password",
                "host": "example.com",
                "port": 88,
                "path": "/path@newexample.net",
                "query": {"foo": "bar"},
                "fragment": "fragment",
            },
        ),
        (
            "https://example.com/|foo=bar",
            {
                "scheme": "https",
                "host": "example.com",
                "path": "/",
                "query": {"foo": "bar"},
                "query_options": QueryOptions(query_separator="|"),
            },
        ),
    ],
)
def test_full(url: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""

    assert_http_parse_expected_vs_url(url, url_components)


def test_calling_parse_on_class() -> None:
    """Test that we can construct URLs correctly."""
    assert HttpUrl.parse("http://example.com") is not None
    assert HttpsUrl.parse("https://example.com") is not None


def test_invalid_scheme() -> None:
    """Test that we can construct URLs correctly."""
    with pytest.raises(ValueError):
        assert_http_parse_expected_vs_url(
            "hodor://example.com", {"scheme": "hodor", "host": "example.com"}
        )

    with pytest.raises(ValueError):
        HttpUrl.parse("hodor://example.com")

    with pytest.raises(ValueError):
        HttpsUrl.parse("hodor://example.com")

    with pytest.raises(ValueError):
        parse_http_or_https_url("hodor://example.com")
