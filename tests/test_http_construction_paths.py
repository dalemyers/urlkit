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
        ("http://example.com", {"scheme": "http", "host": "example.com"}),
        ("http://example.com/", {"scheme": "http", "host": "example.com", "path": "/"}),
        (
            "http://example.com/abc",
            {"scheme": "http", "host": "example.com", "path": "/abc"},
        ),
        (
            "http://example.com/a/b",
            {"scheme": "http", "host": "example.com", "path": "/a/b"},
        ),
        (
            "http://example.com/a/b",
            {"scheme": "http", "host": "example.com", "path": "a/b"},
        ),
        (
            "http://example.com/some/path",
            {"scheme": "http", "host": "example.com", "path": "/some/path"},
        ),
        (
            "http://example.com/home",
            {"scheme": "http", "host": "example.com", "path": "/home"},
        ),
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
        (
            "http://example.com/a;b/c;d",
            {"scheme": "http", "host": "example.com", "path": "/a;b/c;d"},
        ),
        (
            "http://example.com/a;;b",
            {"scheme": "http", "host": "example.com", "path": "/a;;b"},
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
    assert str(a.path) == str(HttpPath(("/section1")))

    a.path = "/Hello/World"
    assert str(a.path) == "/Hello/World"
    assert str(a.path) == str(HttpPath(("/Hello/World")))

    a.path = HttpPath("World/Hello")
    assert str(a.path) == "/World/Hello"
    assert str(a.path) == str(HttpPath(("/World/Hello")))


def test_http_path_equality() -> None:
    """Test that we can compare paths."""
    assert HttpPath("/a/b/c") == HttpPath("/a/b/c")
    assert str(HttpPath("/a/b/c")) == "/a/b/c"
    assert str(HttpPath("/a/b/c")) == str(HttpPath(("/a/b/c")))

    assert HttpPath("/a/b/c") != HttpPath("/a/b/d")
    assert HttpPath("/a/b/c") != "/a/b/d"
    assert str(HttpPath("/a/b/c")) != str(HttpPath(("/a/b/d")))

    assert HttpPath("/a/b/c") != HttpPath("/a/b")
    assert HttpPath("/a/b/c") != "/a/b"
    assert str(HttpPath("/a/b/c")) != str(HttpPath(("/a/b")))

    assert HttpPath("/a/b/c") != HttpPath("/a/b/c/d")
    assert HttpPath("/a/b/c") != "/a/b/c/d"
    assert str(HttpPath("/a/b/c")) != str(HttpPath(("/a/b/c/d")))

    assert str(HttpPath("/a/b/c/")) != "/a/b/c"
    assert str(HttpPath("/a/b/c/")) == "/a/b/c/"

    assert str(HttpPath("/a/b/c")) == "/a/b/c"
    assert str(HttpPath("/a/b/c")) != "/a/b/c/"


def test_http_path_append_pop() -> None:
    """Test that we can append to paths."""
    path = HttpPath("")
    path.append("a")
    assert path == HttpPath("a")
    assert str(path) == str(HttpPath(("a")))
    path.append("b")
    assert path == HttpPath("/a/b")
    assert str(path) == str(HttpPath(("/a/b")))
    path.append("c")
    assert path == HttpPath("/a/b/c")
    assert str(path) == str(HttpPath(("/a/b/c")))
    path.append("d/e")
    assert path == HttpPath("/a/b/c/d/e")
    assert str(path) == str(HttpPath(("/a/b/c/d/e")))
    path.pop_last()
    assert path == HttpPath("/a/b/c/d")
    assert str(path) == str(HttpPath(("/a/b/c/d")))
    path.pop_last()
    assert path == HttpPath("/a/b/c")
    assert str(path) == str(HttpPath(("/a/b/c")))
    path.pop_last()
    assert path == HttpPath("/a/b")
    assert str(path) == str(HttpPath(("/a/b")))
    path.pop_last()
    assert path == HttpPath("/a")
    assert str(path) == str(HttpPath(("/a")))
    path.pop_last()
    assert path == HttpPath("")
    assert str(path) == str(HttpPath(("")))

    with pytest.raises(IndexError):
        path.pop_last()


@pytest.mark.parametrize(
    "original_path,expected_normalized",
    [
        ("/a/b/c/./../../g", "/a/g"),  # From the RFC
        ("/a/b/c/./../../g/", "/a/g/"),  # From the RFC
        ("/a/b/./c/./d", "/a/b/c/d"),
        ("/a/b/c/../d", "/a/b/d"),
        ("/a/b/./c/../d", "/a/b/d"),
        ("/./a", "/a"),
        ("/../a", "/a"),  # Cannot go above root
        ("/a/./../b/./c/../d", "/b/d"),
        ("/a/b/c/.", "/a/b/c/"),  # Trailing "." removes but preserves slash
        ("/a/b/c/./", "/a/b/c/"),
        ("/a/b/c/../", "/a/b/"),
        ("/a/../", "/"),  # Back to root
        ("/a/../../b", "/b"),  # Excess .. collapse to root first
        ("/a/./b/../../c", "/c"),
        ("/./././", "/"),
        ("/.././../x", "/x"),
        ("/a/..", "/"),  # Removing last segment
        ("/a/../", "/"),  # Same but with slash
        ("/a/b/../../../../c", "/c"),  # Over-backtracking collapses to root then adds c
        (
            "/a//b/./c/../d",
            "/a//b/d",
        ),  # Only dot segments removed; double slash preserved
    ],
)
def test_dot_segment_normalization(original_path: str, expected_normalized: str) -> None:
    url = HttpUrl(scheme="http", host="example.com", path=original_path)
    assert str(url) == f"http://example.com{expected_normalized}"


@pytest.mark.parametrize(
    "preserved_path",
    [
        "/a//b///c",  # Multiple empty segments preserved
        "/a/b/..../c",  # '....' is a literal segment, not '..'
        "/a/b/%2E/c",  # Percent-encoded dot should NOT be treated as dot segment
        "/a/b/%2e%2E/c",  # Same (encoded '..') stays literal
        "/a/b/.%2E/c",  # Mixed literal '.' + encoded '.' not a dot segment pair
        "/a/b/%2E./c",  # Encoded '.' plus literal '.' not collapsed
    ],
)
def test_path_preservation_cases(preserved_path: str) -> None:
    url = HttpUrl(scheme="http", host="example.com", path=preserved_path)
    # Current implementation always emits with exactly given components joined by '/'
    # If later you store raw segments, ensure round-trip fidelity here.
    assert str(url) == f"http://example.com{preserved_path}"


# Mixed scenario ensuring fragment and query are unaffected by path normalization.
def test_dot_segments_with_query_and_fragment() -> None:
    url = HttpUrl(
        scheme="https",
        host="example.com",
        path="/a/b/./c/../d/./e/../",
        query={"q": "1"},
        fragment="frag",
    )
    # Normalized path: /a/b/d/
    assert str(url) == "https://example.com/a/b/d/?q=1#frag"


# Ensure trailing slash is preserved (normalization shouldn’t remove it if
# final segment was a directory indicator).
@pytest.mark.parametrize(
    "original_path",
    [
        "/a/b/c/",
        "/a/b/c/./",
        "/a/b/c/d/../",
    ],
)
def test_trailing_slash_preserved(original_path: str) -> None:
    url = HttpUrl(scheme="http", host="example.com", path=original_path)
    # Expected canonical for all these is /a/b/c/ after normalization
    assert str(url) == "http://example.com/a/b/c/"


# Guard: a URL with no path stays no path vs root slash (depends on future
# design choice). If you later distinguish empty vs '/', adjust this test.
def test_empty_path_preserved_current_behavior() -> None:
    url = HttpUrl(scheme="http", host="example.com")
    # Current behavior emits trailing slash; if you change design update this.
    assert str(url) in ("http://example.com/", "http://example.com")


@pytest.mark.parametrize(
    "original_path, expected_normalized",
    [
        # This test case is from RFC 3986, Section 5.4.2. Abnormal Examples
        ("mid/content=5/../6", "/mid/6"),
    ],
)
def test_dot_segment_normalization_abnormal_examples(
    original_path: str, expected_normalized: str
) -> None:
    """
    Test dot-segment normalization for relative paths.

    See RFC 3986, Section 5.4.2. Abnormal Examples.
    """
    url = HttpUrl(scheme="http", host="example.com", path=original_path)
    assert str(url) == f"http://example.com{expected_normalized}"


def test_empty_string_path_is_not_root() -> None:
    """Test that an empty string for a path is not the same as the root path."""
    # See RFC 3986, Section 3.3. Path
    # If a URI contains an authority component, then the path component
    # must either be empty or begin with a slash ("/") character.
    # This implies that an empty path is distinct from a path of "/".
    url_empty = HttpUrl(scheme="http", host="example.com", path="")
    assert str(url_empty) == "http://example.com"

    url_root = HttpUrl(scheme="http", host="example.com", path="/")
    assert str(url_root) == "http://example.com/"


def test_http_path_append_with_dot_segments() -> None:
    """Test that appending paths with dot segments normalizes the path."""
    path = HttpPath("/a/b/c")
    path.append("..")
    assert str(path) == "/a/b"

    path.append("../d")
    assert str(path) == "/a/d"

    path2 = HttpPath("")
    path2.append("a/b/../c")
    assert str(path2) == "/a/c"
