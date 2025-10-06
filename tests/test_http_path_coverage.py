"""Additional tests for uncovered code paths in http_path."""

import pytest

from urlkit.http.http_path import HttpPath


def test_remove_dot_segments_leading_dot_dot_slash() -> None:
    """Test remove_dot_segments with leading ../ pattern."""
    # This tests line 169-170
    result = HttpPath.remove_dot_segments("../a/b")
    assert result == "a/b"

    result2 = HttpPath.remove_dot_segments("../../a")
    assert result2 == "a"


def test_remove_dot_segments_leading_dot_slash() -> None:
    """Test remove_dot_segments with leading ./ pattern."""
    # This tests line 172-173
    result = HttpPath.remove_dot_segments("./a/b")
    assert result == "a/b"

    result2 = HttpPath.remove_dot_segments("././a")
    assert result2 == "a"


def test_remove_dot_segments_just_dots() -> None:
    """Test remove_dot_segments with just dots."""
    # This tests line 191-192
    result = HttpPath.remove_dot_segments(".")
    assert result == ""

    result2 = HttpPath.remove_dot_segments("..")
    assert result2 == ""


def test_http_path_pop_last_leaves_empty_component() -> None:
    """Test pop_last that results in a single empty component."""
    # This tests line 306 (the conditional check)
    path = HttpPath("/a/b/c")
    path.pop_last()  # Remove c
    path.pop_last()  # Remove b
    path.pop_last()  # Remove a

    # After removing all, we should have an empty path
    assert str(path) == ""


def test_http_path_with_none_parameter() -> None:
    """Test HttpPath initialization when path could be None."""
    # While the type hint doesn't allow None, this tests the defensive code at lines 78-79
    # We can't actually pass None due to the type system, but we can test the empty string case
    path = HttpPath("")
    assert len(path._components) == 0
    assert path.trailing_slash is False


def test_remove_dot_segments_relative_no_slash() -> None:
    """Test remove_dot_segments with relative paths without initial slash."""
    # Tests the initial_slash logic
    result = HttpPath.remove_dot_segments("a/./b/../c")
    assert result == "a/c"


def test_remove_dot_segments_complex_relative() -> None:
    """Test remove_dot_segments with complex relative paths."""
    # More complex patterns
    result = HttpPath.remove_dot_segments("../../../a/b")
    assert result == "a/b"

    result2 = HttpPath.remove_dot_segments("./././a/./b")
    assert result2 == "a/b"


def test_http_path_construction_variations() -> None:
    """Test various path construction patterns."""
    # Test paths that exercise different code branches
    p1 = HttpPath("../relative/path")
    assert "../" not in str(p1)  # Should be normalized

    p2 = HttpPath("./relative/path")
    assert "./" not in str(p2)  # Should be normalized

    p3 = HttpPath(".")
    assert str(p3) == ""

    p4 = HttpPath("..")
    assert str(p4) == ""


def test_http_path_normalization_edge_cases() -> None:
    """Test path normalization edge cases."""
    # Test the special case where path == "/"
    path = HttpPath("/")
    assert str(path) == "/"
    assert len(path._components) == 0
    assert path.trailing_slash is True

    # Test empty path vs root
    empty_path = HttpPath("")
    assert str(empty_path) == ""
    assert len(empty_path._components) == 0
    assert empty_path.trailing_slash is False


def test_http_path_with_only_dots() -> None:
    """Test paths that consist only of dot segments."""
    # These should all normalize to empty
    p1 = HttpPath(".")
    assert str(p1) == ""

    p2 = HttpPath("..")
    assert str(p2) == ""

    p3 = HttpPath("./.")
    assert str(p3) == ""

    p4 = HttpPath("../..")
    assert str(p4) == ""


def test_http_path_normalization_additional_edge_cases() -> None:
    """Test additional path normalization edge cases."""
    # Path with just current directory
    p1 = HttpPath(".")
    assert str(p1) == ""

    # Path with just parent directory
    p2 = HttpPath("..")
    assert str(p2) == ""

    # Path starting with ../
    p3 = HttpPath("../foo")
    assert str(p3) == "/foo"

    # Path starting with ./
    p4 = HttpPath("./foo")
    assert str(p4) == "/foo"


def test_http_path_pop_until_empty() -> None:
    """Test popping path components until completely empty."""
    path = HttpPath("/a/b/c")

    popped1 = path.pop_last()
    assert popped1 == "c"

    popped2 = path.pop_last()
    assert popped2 == "b"

    popped3 = path.pop_last()
    assert popped3 == "a"

    # Path should now be empty
    assert str(path) == ""
    assert len(path._components) == 0
