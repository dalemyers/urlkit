"""Test the construction or URLs."""

import os
import sys

import pytest

from utilities import assert_http_construction_expected_vs_components

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from urlkit.http import HttpUrl, HttpPath

# pylint: enable=wrong-import-position


@pytest.mark.parametrize(
    "expected,url_components",
    [
        ("http://example.com/abc", {"scheme": "http", "host": "example.com", "path": "/abc"}),
        (
            "http://example.com/some/path",
            {"scheme": "http", "host": "example.com", "path": "/some/path"},
        ),
        ("http://example.com/home", {"scheme": "http", "host": "example.com", "path": "/home"}),
        ("http://example.com/", {"scheme": "http", "host": "example.com", "path": "/"}),
        # Unusual paths with encoded characters and non-ASCII components
        (
            "http://example.com/files/%E2%9C%93/d%C3%A9tails?status=ok",
            {
                "scheme": "http",
                "host": "example.com",
                "path": "/files/%E2%9C%93/d%C3%A9tails",
                "query": {"status": "ok"},
            },
        ),
        (
            "http://example.com/search?q=%C3%A9l%C3%A9phant&lang=fr#heading",
            {
                "scheme": "http",
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
                "scheme": "http",
                "host": "example.com",
                "path": "//nested///path/to/resource",
                "query": {"step": "5", "retry": "true"},
            },
        ),
        (
            "http://example.com//////weird_path?normalize=false",
            {
                "scheme": "http",
                "host": "example.com",
                "path": "//////weird_path",
                "query": {"normalize": "false"},
            },
        ),
    ],
)
def test_paths(expected: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""
    assert_http_construction_expected_vs_components(expected, url_components)


def test_path_invalid_value() -> None:
    """Test that we can construct URLs correctly."""
    with pytest.raises(TypeError):
        _ = HttpUrl(scheme="http", host="example.com", path=22)  # type: ignore


def test_path_property() -> None:
    """Test that reading back the property gives the same value."""
    a = HttpUrl(scheme="http", host="example.com", path="/section1")
    assert str(a.path) == "/section1"
    assert a.path == HttpPath(components=["section1"], from_root=True)

    a.path = "/Hello/World"
    assert str(a.path) == "/Hello/World"
    assert a.path == HttpPath(components=["Hello", "World"], from_root=True)

    a.path = HttpPath(["World", "Hello"], from_root=True)
    assert str(a.path) == "/World/Hello"
    assert a.path == HttpPath(components=["World", "Hello"], from_root=True)


def test_http_path_equality() -> None:
    """Test that we can compare paths."""
    assert HttpPath(["a", "b", "c"], from_root=False) == HttpPath(["a", "b", "c"], from_root=False)
    assert HttpPath(["a", "b", "c"], from_root=False) != HttpPath(["a", "b", "d"], from_root=False)
    assert HttpPath(["a", "b", "c"], from_root=False) != HttpPath(["a", "b"], from_root=False)
    assert HttpPath(["a", "b", "c"], from_root=False) != HttpPath(
        ["a", "b", "c", "d"], from_root=False
    )
    assert HttpPath(["a", "b", "c"], from_root=False) != "a/b/c"
    assert str(HttpPath(["a", "b", "c"], from_root=False)) == "a/b/c"


def test_http_path_append_pop() -> None:
    """Test that we can append to paths."""
    path = HttpPath([], from_root=False)
    path.append("a")
    assert path == HttpPath(["a"])
    path.append("b")
    assert path == HttpPath(["a", "b"])
    path.append("c")
    assert path == HttpPath(["a", "b", "c"])
    path.append("d/e")
    assert path == HttpPath(["a", "b", "c", "d", "e"])
    path.pop_last()
    assert path == HttpPath(["a", "b", "c", "d"])
    path.pop_last()
    assert path == HttpPath(["a", "b", "c"])
    path.pop_last()
    assert path == HttpPath(["a", "b"])
    path.pop_last()
    assert path == HttpPath(["a"])
    path.pop_last()
    assert path == HttpPath([], from_root=False)

    with pytest.raises(IndexError):
        path.pop_last()
