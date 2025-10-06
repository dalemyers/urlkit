"""Tests for the HttpPath / operator (truediv)."""

# pylint: disable=protected-access

import pytest

from urlkit.http.http_path import HttpPath


def test_truediv_basic_string() -> None:
    """Test basic / operator with a string."""
    path = HttpPath("/api")
    new_path = path / "v1"

    assert str(new_path) == "/api/v1"
    # Original path should not be modified
    assert str(path) == "/api"


def test_truediv_multiple_segments() -> None:
    """Test chaining / operator."""
    path = HttpPath("/api")
    new_path = path / "v1" / "users" / "123"

    assert str(new_path) == "/api/v1/users/123"
    assert str(path) == "/api"


def test_truediv_empty_base_path() -> None:
    """Test / operator starting from empty path."""
    path = HttpPath("")
    new_path = path / "api" / "v1"

    assert str(new_path) == "/api/v1"


def test_truediv_root_path() -> None:
    """Test / operator starting from root path."""
    path = HttpPath("/")
    new_path = path / "api" / "v1"

    # Root path has trailing slash, which is preserved through the first append
    assert str(new_path) == "/api/v1/"


def test_truediv_with_slashes_in_segment() -> None:
    """Test / operator with segment containing slashes."""
    path = HttpPath("/api")
    new_path = path / "v1/users"

    # The append method splits on '/', so this creates multiple segments
    assert str(new_path) == "/api/v1/users"


def test_truediv_with_special_characters() -> None:
    """Test / operator with special characters that need encoding."""
    path = HttpPath("/api")
    new_path = path / "users" / "john doe"

    # Space should be encoded
    assert "john%20doe" in str(new_path)


def test_truediv_preserves_encoding() -> None:
    """Test / operator with pre-encoded segments."""
    path = HttpPath("/api")
    new_path = path / "users" / "john%20doe"

    # The % will be encoded as %25, so %20 becomes %2520
    # This is correct behavior - if you want pre-encoded, use HttpPathComponent directly
    assert str(new_path) == "/api/users/john%2520doe"


def test_truediv_with_http_path() -> None:
    """Test / operator with another HttpPath."""
    path1 = HttpPath("/api/v1")
    path2 = HttpPath("/users/123")

    new_path = path1 / path2

    assert str(new_path) == "/api/v1/users/123"
    # Original paths should not be modified
    assert str(path1) == "/api/v1"
    assert str(path2) == "/users/123"


def test_truediv_with_http_path_trailing_slash() -> None:
    """Test / operator preserves trailing slash from second HttpPath."""
    path1 = HttpPath("/api")
    path2 = HttpPath("/users/")

    new_path = path1 / path2

    assert str(new_path) == "/api/users/"
    assert new_path.trailing_slash is True


def test_truediv_empty_segments() -> None:
    """Test / operator with empty strings."""
    path = HttpPath("/api")
    new_path = path / ""

    # Empty string creates an empty segment, which results in trailing slash
    assert str(new_path) == "/api/"


def test_truediv_multiple_empty_segments() -> None:
    """Test / operator with multiple empty strings."""
    path = HttpPath("/api")
    new_path = path / "" / "v1" / ""

    # Empty strings create empty segments
    assert str(new_path) == "/api/v1//"


def test_truediv_does_not_modify_original() -> None:
    """Test that / operator creates a new path without modifying original."""
    original = HttpPath("/api/v1")
    new_path = original / "users"

    # Modify the new path
    new_path2 = new_path / "123"

    # Original should be unchanged
    assert str(original) == "/api/v1"
    assert str(new_path) == "/api/v1/users"
    assert str(new_path2) == "/api/v1/users/123"


def test_truediv_with_complex_path() -> None:
    """Test / operator with complex path combinations."""
    base = HttpPath("/api/v2")
    middle = HttpPath("/resources/items")
    final = base / middle / "42" / "details"

    assert str(final) == "/api/v2/resources/items/42/details"


def test_truediv_invalid_type() -> None:
    """Test / operator with invalid type raises TypeError."""
    path = HttpPath("/api")

    with pytest.raises(TypeError) as exc_info:
        _ = path / 123  # type: ignore

    assert "unsupported operand type(s) for /" in str(exc_info.value)
    assert "HttpPath" in str(exc_info.value)
    assert "int" in str(exc_info.value)


def test_truediv_with_list_raises_error() -> None:
    """Test / operator with list raises TypeError."""
    path = HttpPath("/api")

    with pytest.raises(TypeError) as exc_info:
        _ = path / ["v1", "users"]  # type: ignore

    assert "unsupported operand type(s) for /" in str(exc_info.value)


def test_truediv_normalization() -> None:
    """Test / operator handles dot segments correctly."""
    path = HttpPath("/api/v1")
    new_path = path / "users" / ".." / "groups"

    # Dot segments should be normalized
    assert str(new_path) == "/api/v1/groups"


def test_truediv_preserves_components_state() -> None:
    """Test / operator preserves encoding state of components."""
    # pylint: disable=import-outside-toplevel,redefined-outer-name,reimported
    from urlkit.http.http_path import HttpPathComponent

    path = HttpPath("/api")
    # Manually add an encoded component
    path._components.append(HttpPathComponent("test%20value", encoded=True))

    new_path = path / "next"

    # The encoded component should still be encoded
    assert "test%20value" in str(new_path)


def test_truediv_realistic_api_pattern() -> None:
    """Test realistic API URL pattern construction."""
    base = HttpPath("/api")
    v1 = base / "v1"
    users = v1 / "users"
    user_id = users / "12345"
    profile = user_id / "profile"

    assert str(base) == "/api"
    assert str(v1) == "/api/v1"
    assert str(users) == "/api/v1/users"
    assert str(user_id) == "/api/v1/users/12345"
    assert str(profile) == "/api/v1/users/12345/profile"


def test_truediv_with_query_like_strings() -> None:
    """Test / operator with strings that look like query parameters."""
    path = HttpPath("/search")
    # Even though this looks like a query, it's part of the path
    # The = will be encoded as %3D
    new_path = path / "q=test"

    assert str(new_path) == "/search/q%3Dtest"


def test_truediv_immutability() -> None:
    """Test that / operator maintains immutability."""
    path1 = HttpPath("/api")
    path2 = path1 / "v1"
    path3 = path1 / "v2"

    # path1 should be unchanged
    assert str(path1) == "/api"
    # path2 and path3 should be independent
    assert str(path2) == "/api/v1"
    assert str(path3) == "/api/v2"


def test_truediv_empty_http_path() -> None:
    """Test / operator with empty HttpPath."""
    path1 = HttpPath("/api")
    path2 = HttpPath("")

    new_path = path1 / path2

    # Empty path shouldn't change anything
    assert str(new_path) == "/api"
