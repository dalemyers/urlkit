"""Test the construction or URLs."""

import os
import sys

import pytest

from utilities import assert_http_parse_expected_vs_url

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from urlkit.http.http_url import HttpUrl, _parse_http_or_https_url, QueryOptions, QuerySet

# pylint: enable=wrong-import-position


# Daniel Stenberg has an interesting post: https://daniel.haxx.se/blog/2022/09/08/http-http-http-http-http-http-http/
# It states that this is a valid URL: http://http://http://@http://http://?http://#http://
# And that this is how it parses:
# scheme: http
# username: http
# password: //http://
# host: http
# port: N/A
# path: //http://
# query: http://
# fragment: http://

# Now, the original version of my parser also agreed with this. However, after
# looking at the RFC, I realized that this parse isn't correct. It ignores rule
# 2.4.3 in RFC 1808 which states:
# If the parse string begins with a double-slash "//", then the
# substring of characters after the double-slash and up to, but not
# including, the next slash "/" character is the network location/login
# (<net_loc>) of the URL.  If no trailing slash "/" is present, the
# entire remaining parse string is assigned to <net_loc>.  The double-
# slash and <net_loc> are removed from the parse string before
# continuing.

# I do like Daniel's parse more, but I've elected to stick to the RFC, so it
# wouldn't parse as CURL/TRURL would.


@pytest.mark.parametrize(
    "url,url_components",
    [
        (
            "http://http://http://@http://http://?http://#http://",
            {
                "scheme": "http",
                "host": "http",
                "path": "//http://@http://http://",
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
            "https://example.com/?",
            {
                "scheme": "https",
                "host": "example.com",
                "path": "/",
                "query": None,
            },
        ),
        (
            "https://example.com/?foo=bar",
            {
                "scheme": "https",
                "host": "example.com",
                "path": "/",
                "query": QuerySet(QueryOptions(), {"foo": "bar"}, assume_unencoded=False),
            },
        ),
        (
            "https://example.com/?foo=bar#fragment",
            {
                "scheme": "https",
                "host": "example.com",
                "path": "/",
                "query": QuerySet(QueryOptions(), {"foo": "bar"}, assume_unencoded=False),
                "fragment": "fragment",
            },
        ),
        (
            "https://example.com/path?foo=bar#fragment",
            {
                "scheme": "https",
                "host": "example.com",
                "path": "/path",
                "query": QuerySet(QueryOptions(), {"foo": "bar"}, assume_unencoded=False),
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
                "query": QuerySet(QueryOptions(), {"foo": "bar"}, assume_unencoded=False),
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
                "query": QuerySet(QueryOptions(), {"foo": "bar"}, assume_unencoded=False),
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
                "query": QuerySet(QueryOptions(), {"foo": "bar"}, assume_unencoded=False),
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
                "query": QuerySet(QueryOptions(), {"foo": "bar"}, assume_unencoded=False),
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
                "query": QuerySet(QueryOptions(), {"foo": "bar"}, assume_unencoded=False),
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
                "query": QuerySet(QueryOptions(), {"foo": "bar"}, assume_unencoded=False),
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
                "query": QuerySet(QueryOptions(), {"foo": "bar"}, assume_unencoded=False),
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
                "query": QuerySet(QueryOptions(), {"foo": "bar"}, assume_unencoded=False),
                "fragment": "fragment",
            },
        ),
        (
            "https://example.com/?foo=bar",
            {
                "scheme": "https",
                "host": "example.com",
                "path": "/",
                "query": QuerySet(QueryOptions(), {"foo": "bar"}, assume_unencoded=False),
                "query_options": QueryOptions(),
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
    assert HttpUrl.parse("https://example.com") is not None


def test_invalid_scheme() -> None:
    """Test that we can construct URLs correctly."""
    with pytest.raises(ValueError):
        assert_http_parse_expected_vs_url(
            "hodor://example.com", {"scheme": "hodor", "host": "example.com"}
        )

    with pytest.raises(ValueError):
        HttpUrl.parse("hodor://example.com")

    with pytest.raises(ValueError):
        _parse_http_or_https_url("hodor://example.com")
