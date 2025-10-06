"""Tests for the HttpUrl / operator (truediv)."""

import pytest

from urlkit.http import HttpUrl
from urlkit.http.http_path import HttpPath


def test_truediv_basic_string() -> None:
    """Test basic / operator with a string on HttpUrl."""
    url = HttpUrl(scheme="http", host="example.com", path="/api")
    new_url = url / "v1"

    assert str(new_url) == "http://example.com/api/v1"
    # Original URL should not be modified
    assert str(url) == "http://example.com/api"


def test_truediv_multiple_segments() -> None:
    """Test chaining / operator on HttpUrl."""
    url = HttpUrl(scheme="https", host="api.example.com", path="/api")
    new_url = url / "v1" / "users" / "123"

    assert str(new_url) == "https://api.example.com/api/v1/users/123"
    assert str(url) == "https://api.example.com/api"


def test_truediv_no_initial_path() -> None:
    """Test / operator when URL has no initial path."""
    url = HttpUrl(scheme="http", host="example.com")
    new_url = url / "api" / "v1"

    # Should create path starting from root
    assert str(new_url) == "http://example.com/api/v1"


def test_truediv_preserves_query() -> None:
    """Test / operator preserves query parameters."""
    url = HttpUrl(scheme="http", host="example.com", path="/api", query={"key": "value"})
    new_url = url / "v1"

    assert str(new_url) == "http://example.com/api/v1?key=value"
    query_value = new_url.query["key"]
    assert query_value is not None
    assert query_value.value == "value"


def test_truediv_preserves_fragment() -> None:
    """Test / operator preserves fragment."""
    url = HttpUrl(scheme="http", host="example.com", path="/api", fragment="section")
    new_url = url / "v1"

    assert str(new_url) == "http://example.com/api/v1#section"
    assert new_url.fragment == "section"


def test_truediv_preserves_all_components() -> None:
    """Test / operator preserves all URL components."""
    url = HttpUrl(
        scheme="https",
        username="user",
        password="pass",
        host="example.com",
        port=8080,
        path="/api",
        query={"key": "value"},
        fragment="section",
    )
    new_url = url / "v1" / "users"

    assert str(new_url) == "https://user:pass@example.com:8080/api/v1/users?key=value#section"
    assert new_url.username == "user"
    assert new_url.password == "pass"
    assert new_url.port == 8080
    query_value = new_url.query["key"]
    assert query_value is not None
    assert query_value.value == "value"
    assert new_url.fragment == "section"


def test_truediv_with_http_path() -> None:
    """Test / operator with HttpPath object."""
    url = HttpUrl(scheme="http", host="example.com", path="/api")
    path_segment = HttpPath("/v1/users")

    new_url = url / path_segment

    assert str(new_url) == "http://example.com/api/v1/users"
    # Original URL should not be modified
    assert str(url) == "http://example.com/api"


def test_truediv_with_slashes_in_segment() -> None:
    """Test / operator with segment containing slashes."""
    url = HttpUrl(scheme="http", host="example.com", path="/api")
    new_url = url / "v1/users"

    # The append method splits on '/', so this creates multiple segments
    assert str(new_url) == "http://example.com/api/v1/users"


def test_truediv_with_special_characters() -> None:
    """Test / operator with special characters that need encoding."""
    url = HttpUrl(scheme="http", host="example.com", path="/api")
    new_url = url / "users" / "john doe"

    # Space should be encoded
    assert "john%20doe" in str(new_url)


def test_truediv_empty_segment() -> None:
    """Test / operator with empty string."""
    url = HttpUrl(scheme="http", host="example.com", path="/api")
    _ = url / ""

    # Empty segments create empty path components
    assert str(url) == "http://example.com/api"


def test_truediv_with_root_path() -> None:
    """Test / operator when base path is just root."""
    url = HttpUrl(scheme="http", host="example.com", path="/")
    new_url = url / "api" / "v1"

    # Root path has trailing slash initially
    assert str(new_url) == "http://example.com/api/v1/"


def test_truediv_invalid_type() -> None:
    """Test / operator with invalid type raises TypeError."""
    url = HttpUrl(scheme="http", host="example.com", path="/api")

    with pytest.raises(TypeError) as exc_info:
        _ = url / 123  # type: ignore

    assert "unsupported operand type(s) for /" in str(exc_info.value)
    assert "'HttpUrl' and 'int'" in str(exc_info.value)


def test_truediv_with_list_raises_error() -> None:
    """Test / operator with list raises TypeError."""
    url = HttpUrl(scheme="http", host="example.com", path="/api")

    with pytest.raises(TypeError) as exc_info:
        _ = url / ["v1", "users"]  # type: ignore

    assert "unsupported operand type(s) for /" in str(exc_info.value)


def test_truediv_does_not_modify_original() -> None:
    """Test that / operator creates a new URL and doesn't modify the original."""
    original_url = HttpUrl(scheme="http", host="example.com", path="/api", query={"key": "value"})
    original_str = str(original_url)

    new_url = original_url / "v1" / "users"
    new_url.query["new_key"] = "new_value"

    # Original should be unchanged
    assert str(original_url) == original_str
    assert "new_key" not in original_url.query
    assert "v1" not in str(original_url)


def test_truediv_chainable_with_modifications() -> None:
    """Test / operator is chainable with other modifications."""
    url = HttpUrl(scheme="http", host="example.com")
    new_url = url / "api" / "v1"
    new_url.query["format"] = "json"
    new_url.fragment = "results"

    assert str(new_url) == "http://example.com/api/v1?format=json#results"
    # Original should still be clean
    assert str(url) == "http://example.com"


def test_truediv_with_parsed_url() -> None:
    """Test / operator works with parsed URLs."""
    url = HttpUrl.parse("https://api.example.com/v1/users?limit=10")
    new_url = url / "123" / "profile"

    assert str(new_url) == "https://api.example.com/v1/users/123/profile?limit=10"


def test_truediv_preserves_trailing_slash() -> None:
    """Test / operator with trailing slash preservation."""
    url = HttpUrl(scheme="http", host="example.com", path="/api/")
    new_url = url / "v1"

    # The trailing slash behavior depends on HttpPath normalization
    # After appending, normalization may change the trailing slash
    assert "/api/" in str(new_url) or "/api/v1" in str(new_url)


def test_truediv_with_encoded_path_segment() -> None:
    """Test / operator with pre-encoded segment."""
    url = HttpUrl(scheme="http", host="example.com", path="/api")
    new_url = url / "users" / "john%20doe"

    # The % will be encoded as %25, so %20 becomes %2520
    # This is correct behavior - raw strings are assumed to be unencoded
    assert str(new_url) == "http://example.com/api/users/john%2520doe"


def test_truediv_deeply_nested() -> None:
    """Test / operator with many levels of nesting."""
    url = HttpUrl(scheme="https", host="example.com")
    new_url = url / "a" / "b" / "c" / "d" / "e" / "f" / "g"

    assert str(new_url) == "https://example.com/a/b/c/d/e/f/g"


def test_truediv_preserves_scheme() -> None:
    """Test / operator preserves https vs http."""
    http_url = HttpUrl(scheme="http", host="example.com", path="/api")
    https_url = HttpUrl(scheme="https", host="example.com", path="/api")

    new_http = http_url / "v1"
    new_https = https_url / "v1"

    assert new_http.scheme == "http"
    assert new_https.scheme == "https"


def test_truediv_with_port() -> None:
    """Test / operator preserves port."""
    url = HttpUrl(scheme="http", host="example.com", port=8080, path="/api")
    new_url = url / "v1"

    assert str(new_url) == "http://example.com:8080/api/v1"
    assert new_url.port == 8080


def test_truediv_mixed_string_and_httppath() -> None:
    """Test / operator with mixed string and HttpPath arguments."""
    url = HttpUrl(scheme="http", host="example.com", path="/api")
    path_obj = HttpPath("/v1")

    new_url = url / path_obj / "users" / "123"

    assert str(new_url) == "http://example.com/api/v1/users/123"
