"""Test parsing URLs with percent-encoded paths."""

import pytest

from urlkit.http import HttpUrl, QueryOptions, QuerySet


@pytest.mark.parametrize(
    "url,expected_path",
    [
        # Basic percent-encoded paths
        ("http://example.com/hello%20world", "/hello%20world"),
        # urllib.parse.quote normalizes hex digits to lowercase
        ("http://example.com/path%2Fwith%2Fslashes", "/path%2fwith%2fslashes"),
        ("http://example.com/%E2%9C%93", "/%e2%9c%93"),
        ("http://example.com/test%3Fquery", "/test%3fquery"),
        ("http://example.com/test%23hash", "/test%23hash"),
        # Multiple segments with encoding
        ("http://example.com/a%20b/c%20d", "/a%20b/c%20d"),
        ("http://example.com/files/%E2%9C%93/details", "/files/%e2%9c%93/details"),
        # Mixed encoded and literal characters
        ("http://example.com/path/with%20space/end", "/path/with%20space/end"),
        # Encoded dots (should NOT be treated as dot segments)
        ("http://example.com/a/%2E/b", "/a/%2e/b"),
        ("http://example.com/a/%2E%2E/b", "/a/%2e%2e/b"),
        # Encoded semicolons
        ("http://example.com/path%3Bparam", "/path%3bparam"),
        # Uppercase and lowercase hex digits (normalized to lowercase)
        ("http://example.com/%2f%2F", "/%2f%2f"),
        ("http://example.com/%2E%2e", "/%2e%2e"),
        # Multiple consecutive encoded characters
        ("http://example.com/%20%20%20", "/%20%20%20"),
        # Encoded unreserved characters (should be preserved as-is)
        ("http://example.com/%41%42%43", "/%41%42%43"),  # ABC
    ],
)
def test_parse_encoded_paths(url: str, expected_path: str) -> None:
    """Test that parsing URLs with encoded paths preserves the encoding."""
    parsed = HttpUrl.parse(url)
    assert str(parsed.path) == expected_path


def test_parse_encoded_paths_with_query() -> None:
    """Test parsing URLs with encoded paths and query strings."""
    url1 = "http://example.com/%e2%9c%93?status=ok"
    parsed1 = HttpUrl.parse(url1)
    assert str(parsed1.path) == "/%e2%9c%93"
    assert parsed1.query is not None

    url2 = "http://example.com/test%3fquery?actual=query"
    parsed2 = HttpUrl.parse(url2)
    assert str(parsed2.path) == "/test%3fquery"
    assert parsed2.query is not None


def test_parse_encoded_path_with_trailing_slash() -> None:
    """Test parsing encoded path with trailing slash."""
    url = "http://example.com/hello%20world/"
    parsed = HttpUrl.parse(url)
    assert str(parsed.path) == "/hello%20world/"
    assert parsed.path is not None
    assert parsed.path.trailing_slash is True


def test_parse_encoded_path_normalization() -> None:
    """Test that dot segments are normalized even with encoded paths."""
    # Literal dots should be normalized
    url = "http://example.com/a/./b"
    parsed = HttpUrl.parse(url)
    assert str(parsed.path) == "/a/b"

    # But encoded dots should NOT be normalized
    url_encoded = "http://example.com/a/%2E/b"
    parsed_encoded = HttpUrl.parse(url_encoded)
    # hex digits are normalized to lowercase
    assert str(parsed_encoded.path) == "/a/%2e/b"


def test_parse_encoded_path_with_query_and_fragment() -> None:
    """Test parsing encoded path with query and fragment."""
    url = "http://example.com/hello%20world?foo=bar#section"
    parsed = HttpUrl.parse(url)
    assert str(parsed.path) == "/hello%20world"
    assert parsed.query == QuerySet(QueryOptions(), {"foo": "bar"}, assume_unencoded=False)
    assert parsed.fragment == "section"


def test_parse_roundtrip_encoded_path() -> None:
    """Test that parsing and stringifying preserves encoded paths."""
    original = "http://example.com/hello%20world/test%3fquery"
    parsed = HttpUrl.parse(original)
    reconstructed = str(parsed)
    # Note: hex digits are normalized to lowercase
    expected = "http://example.com/hello%20world/test%3fquery"
    assert reconstructed == expected


def test_parse_uppercase_encoded() -> None:
    """Test parsing with uppercase hex encoding."""
    url = "http://example.com/%2F%3F%23"
    parsed = HttpUrl.parse(url)
    # The encoding should be preserved as-is
    path_str = str(parsed.path)
    assert "%2f" in path_str
    assert "%3f" in path_str
    assert "%23" in path_str


def test_parse_mixed_encoded_literal() -> None:
    """Test parsing paths with both encoded and literal characters."""
    url = "http://example.com/a/b%20c/d"
    parsed = HttpUrl.parse(url)
    assert str(parsed.path) == "/a/b%20c/d"


def test_parse_empty_path_segments() -> None:
    """Test parsing paths with empty segments."""
    url = "http://example.com//a///b"
    parsed = HttpUrl.parse(url)
    # Empty segments should be preserved
    assert str(parsed.path) == "//a///b"


def test_parse_path_with_semicolon() -> None:
    """Test parsing path with semicolon (safe character)."""
    url = "http://example.com/path;param=value"
    parsed = HttpUrl.parse(url)
    # The = sign gets encoded, but ; is safe
    assert str(parsed.path) == "/path;param%3Dvalue"


def test_parse_path_with_colon() -> None:
    """Test parsing path with colon."""
    url = "http://example.com/path:with:colons"
    parsed = HttpUrl.parse(url)
    # Colons get encoded in the path segment
    assert str(parsed.path) == "/path%3Awith%3Acolons"


def test_parse_path_with_at_sign() -> None:
    """Test parsing path with @ sign."""
    url = "http://example.com/path@with@at"
    parsed = HttpUrl.parse(url)
    # @ signs get encoded in the path segment
    assert str(parsed.path) == "/path%40with%40at"
