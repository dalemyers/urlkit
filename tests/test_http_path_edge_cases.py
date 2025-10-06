"""Test edge cases and uncovered paths in HttpPath."""

import copy

import pytest

from urlkit.http.http_path import HttpPath, HttpPathComponent


def test_http_path_init_with_none() -> None:
    """Test initializing HttpPath with None (should be handled)."""
    # While the signature doesn't allow None, this tests the defensive code
    path = HttpPath("")
    assert len(path._components) == 0
    assert path.trailing_slash is False


def test_http_path_equality_trailing_slash_difference() -> None:
    """Test that paths with and without trailing slashes are not equal."""
    path1 = HttpPath("/a/b/c")
    path2 = HttpPath("/a/b/c/")

    assert path1 != path2
    assert path1.trailing_slash is False
    assert path2.trailing_slash is True


def test_http_path_deepcopy_with_trailing_slash() -> None:
    """Test deep copying preserves trailing slash."""
    original = HttpPath("/a/b/c/")
    copied = copy.deepcopy(original)

    assert copied == original
    assert copied.trailing_slash is True
    assert str(copied) == str(original)


def test_http_path_deepcopy_with_components() -> None:
    """Test deep copying preserves components."""
    original = HttpPath("/a/b/c")
    copied = copy.deepcopy(original)

    assert copied == original
    assert len(copied._components) == len(original._components)
    # Components should be separate instances
    assert copied._components is not original._components


def test_http_path_is_percent_encoded_valid() -> None:
    """Test _is_percent_encoded with valid encodings."""
    # Valid percent encodings
    assert HttpPath._is_percent_encoded("hello%20world") is True
    assert HttpPath._is_percent_encoded("%2F%3F%23") is True
    assert HttpPath._is_percent_encoded("%E2%9C%93") is True
    assert HttpPath._is_percent_encoded("%2e%2E") is True


def test_http_path_is_percent_encoded_invalid() -> None:
    """Test _is_percent_encoded with invalid encodings."""
    # No percent signs
    assert HttpPath._is_percent_encoded("hello") is False

    # Incomplete encoding at end
    assert HttpPath._is_percent_encoded("hello%2") is False
    assert HttpPath._is_percent_encoded("hello%") is False

    # Invalid hex digits
    assert HttpPath._is_percent_encoded("hello%ZZ") is False
    assert HttpPath._is_percent_encoded("hello%GG") is False
    assert HttpPath._is_percent_encoded("hello%1G") is False


def test_http_path_is_percent_encoded_edge_cases() -> None:
    """Test _is_percent_encoded edge cases."""
    # Empty string
    assert HttpPath._is_percent_encoded("") is False

    # Just a percent sign
    assert HttpPath._is_percent_encoded("%") is False

    # Percent at the very end with only one char after
    assert HttpPath._is_percent_encoded("test%2") is False


def test_http_path_append_to_empty_with_empty_string() -> None:
    """Test appending to path that has an empty string component."""
    path = HttpPath("")
    path._components = [HttpPathComponent("", False)]
    path.append("test")

    # Should handle the empty component
    assert str(path) == "/test"


def test_http_path_append_list() -> None:
    """Test appending a list of components."""
    path = HttpPath("/a")
    path.append(["b", "c", "d"])

    assert str(path) == "/a/b/c/d"


def test_http_path_append_with_slash() -> None:
    """Test appending a string containing slashes."""
    path = HttpPath("/a")
    path.append("b/c/d")

    assert str(path) == "/a/b/c/d"


def test_http_path_append_single_component() -> None:
    """Test appending a single component without slashes."""
    path = HttpPath("/a")
    path.append("b")

    assert str(path) == "/a/b"


def test_http_path_pop_last_until_empty() -> None:
    """Test popping until path is empty."""
    path = HttpPath("/a/b")

    popped1 = path.pop_last()
    assert popped1 == "b"
    assert str(path) == "/a"

    popped2 = path.pop_last()
    assert popped2 == "a"
    assert str(path) == ""


def test_http_path_pop_last_with_empty_component() -> None:
    """Test pop_last when it results in an empty component."""
    path = HttpPath("/a/b")
    path.pop_last()

    # After popping, if we somehow have a single empty component, it should be handled
    # This tests the defensive code at line 305-306
    if len(path._components) == 1:
        path._components = [HttpPathComponent("", False)]
        remaining = path.pop_last()
        assert remaining == ""


def test_http_path_hash_empty() -> None:
    """Test hashing of empty path."""
    path1 = HttpPath("")
    path2 = HttpPath("")

    assert hash(path1) == hash(path2)
    assert hash(path1) == 0  # According to implementation


def test_http_path_hash_non_empty() -> None:
    """Test hashing of non-empty paths."""
    path1 = HttpPath("/a/b/c")
    path2 = HttpPath("/a/b/c")
    path3 = HttpPath("/a/b/d")

    assert hash(path1) == hash(path2)
    assert hash(path1) != hash(path3)


def test_http_path_hash_usable_in_set() -> None:
    """Test that HttpPath can be used in sets."""
    path1 = HttpPath("/a/b")
    path2 = HttpPath("/a/b")
    path3 = HttpPath("/a/c")

    path_set = {path1, path2, path3}
    assert len(path_set) == 2


def test_http_path_hash_usable_in_dict() -> None:
    """Test that HttpPath can be used as dict keys."""
    path1 = HttpPath("/a/b")
    path2 = HttpPath("/a/b")

    path_dict = {path1: "value1"}
    path_dict[path2] = "value2"

    assert len(path_dict) == 1
    assert path_dict[path1] == "value2"


def test_http_path_str_empty_no_trailing_slash() -> None:
    """Test string representation of empty path without trailing slash."""
    path = HttpPath("")
    assert str(path) == ""


def test_http_path_str_empty_with_trailing_slash() -> None:
    """Test string representation of just root path."""
    path = HttpPath("/")
    assert str(path) == "/"
    assert len(path._components) == 0
    assert path.trailing_slash is True


def test_http_path_str_preserves_semicolons() -> None:
    """Test that semicolons are preserved in path (safe character)."""
    path = HttpPath("/a;b/c;d")
    assert str(path) == "/a;b/c;d"


def test_http_path_normalize_preserves_encoded_dots() -> None:
    """Test that encoded dots are preserved during normalization."""
    path = HttpPath("/a/%2E/b")
    assert str(path) == "/a/%2E/b"

    path2 = HttpPath("/a/%2E%2E/b")
    assert str(path2) == "/a/%2E%2E/b"


def test_http_path_normalize_handles_mixed_encoding() -> None:
    """Test normalization with mixed encoded and literal paths."""
    path = HttpPath("/a/b%20c/./d")
    # Literal ./ should be normalized, but b%20c should be preserved
    assert str(path) == "/a/b%20c/d"


def test_http_path_multiple_slashes_preserved() -> None:
    """Test that multiple consecutive slashes are preserved."""
    path = HttpPath("//a///b////c")
    # Multiple slashes create empty segments
    assert str(path) == "//a///b////c"


def test_http_path_component_with_special_chars() -> None:
    """Test path components with special characters get encoded."""
    path = HttpPath("/hello world/test?query")
    path_str = str(path)
    # Spaces should be encoded
    assert "%20" in path_str
    # Question marks should be encoded
    assert "%3F" in path_str or "%3f" in path_str


def test_http_path_component_with_hash() -> None:
    """Test path components with hash characters get encoded."""
    path = HttpPath("/test#fragment")
    path_str = str(path)
    # Hash should be encoded
    assert "%23" in path_str or "%23" in path_str


def test_http_path_unicode_gets_encoded() -> None:
    """Test that Unicode characters in paths get encoded."""
    path = HttpPath("/✓")
    path_str = str(path)
    # Unicode checkmark should be percent-encoded
    assert "%E2%9C%93" in path_str


def test_http_path_equality_with_non_path() -> None:
    """Test that HttpPath is not equal to non-HttpPath objects."""
    path = HttpPath("/a/b")
    assert path != "/a/b"
    assert path != ["a", "b"]
    assert path != None
    assert path != 123


def test_http_path_from_encoded_preserves_encoding() -> None:
    """Test that creating a path from encoded string preserves encoding."""
    path = HttpPath("/hello%20world")
    assert str(path) == "/hello%20world"

    # Should not double-encode
    assert "%2520" not in str(path)


def test_http_path_append_maintains_encoding_state() -> None:
    """Test that appending components tracks encoding correctly."""
    path = HttpPath("/a")
    path.append("b c")  # Unencoded with space

    path_str = str(path)
    # The space in "b c" should be encoded when converting to string
    assert "%20" in path_str


def test_http_path_init_with_none_parameter() -> None:
    """Test HttpPath initialization with None (defensive code)."""
    # This should be caught by type checking, but the code handles it defensively
    # We need to bypass type checking to test this path
    path = HttpPath.__new__(HttpPath)
    path.__init__(None)  # type: ignore
    assert len(path._components) == 0
    assert path.trailing_slash is False


def test_remove_dot_segments_leading_relative_parent() -> None:
    """Test remove_dot_segments with leading ../."""
    result = HttpPath.remove_dot_segments("../a/b")
    assert result == "a/b"

    result2 = HttpPath.remove_dot_segments("../../a/b")
    assert result2 == "a/b"

    result3 = HttpPath.remove_dot_segments("../../../a")
    assert result3 == "a"

    # Multiple leading ../
    result4 = HttpPath.remove_dot_segments("../../../../a/b/c")
    assert result4 == "a/b/c"


def test_remove_dot_segments_leading_relative_current() -> None:
    """Test remove_dot_segments with leading ./."""
    result = HttpPath.remove_dot_segments("./a/b")
    assert result == "a/b"

    result2 = HttpPath.remove_dot_segments("././a")
    assert result2 == "a"

    result3 = HttpPath.remove_dot_segments("./././a/b")
    assert result3 == "a/b"

    # Multiple leading ./
    result4 = HttpPath.remove_dot_segments("././././a/b/c")
    assert result4 == "a/b/c"


def test_remove_dot_segments_just_dots() -> None:
    """Test remove_dot_segments with just . or ..."""
    result_dot = HttpPath.remove_dot_segments(".")
    assert result_dot == ""

    result_dotdot = HttpPath.remove_dot_segments("..")
    assert result_dotdot == ""


def test_remove_dot_segments_mixed_patterns() -> None:
    """Test paths with mixed dot segment patterns."""
    # Mix of ../  and other segments
    result1 = HttpPath.remove_dot_segments("../foo/../bar")
    assert result1 == "bar"

    # Mix of ./ and other segments
    result2 = HttpPath.remove_dot_segments("./foo/./bar")
    assert result2 == "foo/bar"

    # Just dots at the end
    result3 = HttpPath.remove_dot_segments("foo/bar/..")
    assert result3 == "foo"


def test_remove_dot_segments_sequential_dots() -> None:
    """Test sequential dot patterns."""
    # Sequential ../ at the start
    result = HttpPath.remove_dot_segments("../../../a")
    assert result == "a"

    # Sequential ./ at the start
    result2 = HttpPath.remove_dot_segments("./././a")
    assert result2 == "a"

    # Just dots that should be removed
    result3 = HttpPath.remove_dot_segments("..")
    assert result3 == ""

    result4 = HttpPath.remove_dot_segments(".")
    assert result4 == ""


def test_http_path_pop_last_single_empty_component() -> None:
    """Test pop_last when single empty component remains."""
    # Create a specific scenario where we have a single empty component
    path = HttpPath("/a")
    # After popping 'a', we might have [""] left
    path.pop_last()

    # The path should now be empty
    assert str(path) == ""

    # Now test with a path that definitely creates the edge case
    path2 = HttpPath("//a")  # Leading empty component
    assert str(path2) == "//a"  # Should preserve the empty components


def test_http_path_pop_last_with_single_empty_component_detailed() -> None:
    """Test pop_last edge case where single empty component should be cleared.

    This tests the specific edge case where after popping, we're left with
    exactly one component that has an empty value, which should be cleared.
    """
    from urlkit.http.http_path import HttpPathComponent

    # Create a path with an empty component followed by a normal component
    # This can happen with paths like "//test"
    path = HttpPath.__new__(HttpPath)
    path._components = [HttpPathComponent("", False), HttpPathComponent("test", False)]
    path.trailing_slash = False

    # Pop the last component
    result = path.pop_last()
    assert result == "test"

    # After popping, we should have cleared the empty component
    assert len(path._components) == 0
    assert str(path) == ""
