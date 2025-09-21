"""Test the construction or URLs."""

import pytest

from utilities import assert_http_construction_expected_vs_components


@pytest.mark.parametrize(
    "expected,url_components",
    [
        (
            "http://example.com:8080/some/path?name=alice#section1",
            {
                "scheme": "http",
                "host": "example.com",
                "port": 8080,
                "path": "/some/path",
                "query": {"name": "alice"},
                "fragment": "section1",
            },
        ),
        (
            "http://example.com:443/home?search=python&lang=en#top",
            {
                "scheme": "http",
                "host": "example.com",
                "port": 443,
                "path": "/home",
                "query": {"search": "python", "lang": "en"},
                "fragment": "top",
            },
        ),
        (
            "http://example.com?search=python#footer",
            {
                "scheme": "http",
                "host": "example.com",
                "query": "search=python",
                "fragment": "footer",
            },
        ),
        # Complex paths with query strings and fragments
        (
            "http://example.com/api/v1/users/123?active=true&role=admin#profile",
            {
                "scheme": "http",
                "host": "example.com",
                "path": "/api/v1/users/123",
                "query": {"active": "true", "role": "admin"},
                "fragment": "profile",
            },
        ),
        (
            "http://example.com:9000/docs/index.html?view=full&page=2#introduction",
            {
                "scheme": "http",
                "host": "example.com",
                "port": 9000,
                "path": "/docs/index.html",
                "query": {"view": "full", "page": 2},
                "fragment": "introduction",
            },
        ),
        # Combining IPv6 address with ports, paths, and fragments
        (
            "http://[2001:db8::1]:8080/status?check=true#up",
            {
                "scheme": "http",
                "host": "[2001:db8::1]",
                "port": 8080,
                "path": "/status",
                "query": {"check": "true"},
                "fragment": "up",
            },
        ),
        (
            "http://[::1]:3000/settings?debug=true",
            {
                "scheme": "http",
                "host": "[::1]",
                "port": 3000,
                "path": "/settings",
                "query": {"debug": "true"},
            },
        ),
        # Multiple levels of fragments
        (
            "http://example.com/user/settings#privacy#password",
            {
                "scheme": "http",
                "host": "example.com",
                "path": "/user/settings",
                "fragment": "privacy#password",
            },
        ),
        # Multiple combinations of paths, queries, fragments, and ports
        (
            "http://example.com:8081/checkout/cart/view?items=5&coupon=special&discount=10#summary",
            {
                "scheme": "http",
                "host": "example.com",
                "port": 8081,
                "path": "/checkout/cart/view",
                "query": {"items": "5", "coupon": "special", "discount": "10"},
                "fragment": "summary",
            },
        ),
    ],
)
def test_full(expected: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""
    assert_http_construction_expected_vs_components(expected, url_components)


@pytest.mark.parametrize(
    "expected,url_components",
    [
        (
            "http://example.com",
            {
                "scheme": "http",
                "host": "example.com",
                "path": None,
                "query": None,
                "fragment": None,
            },
        ),
        ("http://localhost", {"scheme": "http", "host": "localhost"}),
        ("http://127.0.0.1", {"scheme": "http", "host": "127.0.0.1"}),
        ("http://[::1]", {"scheme": "http", "host": "[::1]"}),  # IPv6 address
    ],
)
def test_full_edge_cases(expected: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""
    assert_http_construction_expected_vs_components(expected, url_components)
