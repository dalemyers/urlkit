"""Test the construction or URLs."""

import os
import sys

import pytest

from utilities import assert_http_expected_vs_components

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from urlkit.http_url import HttpUrl

# pylint: enable=wrong-import-position


@pytest.mark.parametrize(
    "expected,url_components",
    [
        ("http://example.com/abc", {"host": "example.com", "path": "/abc"}),
        ("http://example.com/some/path", {"host": "example.com", "path": "/some/path"}),
        ("http://example.com/home", {"host": "example.com", "path": "/home"}),
        ("http://example.com/", {"host": "example.com", "path": "/"}),
        # Unusual paths with encoded characters and non-ASCII components
        (
            "http://example.com/files/%E2%9C%93/d%C3%A9tails?status=ok",
            {
                "host": "example.com",
                "path": "/files/%E2%9C%93/d%C3%A9tails",
                "query": {"status": "ok"},
            },
        ),
        (
            "http://example.com/search?q=%C3%A9l%C3%A9phant&lang=fr#heading",
            {
                "host": "example.com",
                "path": "/search",
                "query": {"q": "éléphant", "lang": "fr"},
                "fragment": "heading",
            },
        ),
        # Paths with multiple slashes and unusual directory structure
        (
            "http://example.com//nested///path/to/resource?step=5&retry=true",
            {
                "host": "example.com",
                "path": "//nested///path/to/resource",
                "query": {"step": "5", "retry": "true"},
            },
        ),
        (
            "http://example.com//////weird_path?normalize=false",
            {
                "host": "example.com",
                "path": "//////weird_path",
                "query": {"normalize": "false"},
            },
        ),
    ],
)
def test_paths(expected: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""
    assert_http_expected_vs_components(expected, url_components)


def test_path_invalid_value() -> None:
    """Test that we can construct URLs correctly."""
    with pytest.raises(TypeError):
        _ = HttpUrl(host="example.com", path=22)  # type: ignore


def test_path_property() -> None:
    """Test that reading back the property gives the same value."""
    a = HttpUrl(host="example.com", path="/section1")
    assert a.path == "/section1"
