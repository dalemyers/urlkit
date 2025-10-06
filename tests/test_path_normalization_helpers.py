"""Tests for the path normalization helper methods."""

# pylint: disable=protected-access

from urlkit.http.http_path import HttpPath


# _process_dot_segment_pattern tests
def test_process_dot_segment_slash_dot_slash() -> None:
    """Test processing '/./' pattern."""
    segments: list[str] = []
    result = HttpPath._process_dot_segment_pattern("/./rest", segments)

    assert result == "/rest"
    assert not segments


def test_process_dot_segment_slash_dot_end() -> None:
    """Test processing '/.' at end of path."""
    segments: list[str] = []
    result = HttpPath._process_dot_segment_pattern("/.", segments)

    assert result == "/"
    assert not segments


def test_process_dot_segment_slash_dotdot_slash() -> None:
    """Test processing '/../' pattern."""
    segments = ["a", "b"]
    result = HttpPath._process_dot_segment_pattern("/../rest", segments)

    assert result == "/rest"
    assert segments == ["a"]  # "b" was popped


def test_process_dot_segment_slash_dotdot_slash_empty_segments() -> None:
    """Test processing '/../' pattern with empty segments list."""
    segments: list[str] = []
    result = HttpPath._process_dot_segment_pattern("/../rest", segments)

    assert result == "/rest"
    assert not segments  # Nothing to pop


def test_process_dot_segment_slash_dotdot_end() -> None:
    """Test processing '/..' at end of path."""
    segments = ["a", "b", "c"]
    result = HttpPath._process_dot_segment_pattern("/..", segments)

    assert result == ""
    assert segments == ["a", "b"]  # "c" was popped


def test_process_dot_segment_slash_dotdot_end_empty_segments() -> None:
    """Test processing '/..' at end with empty segments."""
    segments: list[str] = []
    result = HttpPath._process_dot_segment_pattern("/..", segments)

    assert result == ""
    assert not segments


def test_process_dot_segment_no_match() -> None:
    """Test that non-matching patterns return None."""
    segments: list[str] = []
    result = HttpPath._process_dot_segment_pattern("/normal/path", segments)

    assert result is None
    assert not segments


def test_process_dot_segment_similar_but_not_matching() -> None:
    """Test patterns that look similar but don't match."""
    segments: list[str] = []

    # "..." is not a dot segment
    result = HttpPath._process_dot_segment_pattern("/...", segments)
    assert result is None

    # "./" without leading slash is not matched (handled elsewhere)
    result = HttpPath._process_dot_segment_pattern("./path", segments)
    assert result is None


def test_process_dot_segment_multiple_pops() -> None:
    """Test multiple '../' patterns in sequence."""
    segments = ["a", "b", "c", "d"]

    # First ../
    result = HttpPath._process_dot_segment_pattern("/../more", segments)
    assert result == "/more"
    assert segments == ["a", "b", "c"]

    # Second ../
    result = HttpPath._process_dot_segment_pattern("/../more", segments)
    assert result == "/more"
    assert segments == ["a", "b"]


# _extract_next_segment tests
def test_extract_next_segment_simple() -> None:
    """Test extracting a simple segment."""
    segment, remaining = HttpPath._extract_next_segment("/api/v1")

    assert segment == "api"
    assert remaining == "/v1"


def test_extract_next_segment_last() -> None:
    """Test extracting the last segment."""
    segment, remaining = HttpPath._extract_next_segment("/last")

    assert segment == "last"
    assert remaining == ""


def test_extract_next_segment_with_trailing_slash() -> None:
    """Test extracting segment when path ends with slash."""
    segment, remaining = HttpPath._extract_next_segment("/segment/")

    assert segment == "segment"
    assert remaining == "/"


def test_extract_next_segment_empty_segment() -> None:
    """Test extracting empty segment (double slash)."""
    segment, remaining = HttpPath._extract_next_segment("//next")

    assert segment == ""
    assert remaining == "/next"


def test_extract_next_segment_single_char() -> None:
    """Test extracting single character segment."""
    segment, remaining = HttpPath._extract_next_segment("/a/b/c")

    assert segment == "a"
    assert remaining == "/b/c"


def test_extract_next_segment_long_segment() -> None:
    """Test extracting a long segment name."""
    segment, remaining = HttpPath._extract_next_segment("/very-long-segment-name/next")

    assert segment == "very-long-segment-name"
    assert remaining == "/next"


def test_extract_next_segment_special_chars() -> None:
    """Test extracting segment with special characters."""
    segment, remaining = HttpPath._extract_next_segment("/segment-with_special.chars/next")

    assert segment == "segment-with_special.chars"
    assert remaining == "/next"


def test_extract_next_segment_encoded_chars() -> None:
    """Test extracting segment with percent-encoded characters."""
    segment, remaining = HttpPath._extract_next_segment("/hello%20world/next")

    assert segment == "hello%20world"
    assert remaining == "/next"


# Integration tests using remove_dot_segments
def test_integration_complex_path_normalization() -> None:
    """Test complex path normalization using the refactored helpers."""
    # RFC 3986 example
    result = HttpPath.remove_dot_segments("/a/b/c/./../../g")
    assert result == "/a/g"


def test_integration_all_dots() -> None:
    """Test path with only dot segments."""
    result = HttpPath.remove_dot_segments("/./././.")
    assert result == "/"


def test_integration_leading_dotdots() -> None:
    """Test path starting with parent references."""
    result = HttpPath.remove_dot_segments("/../../../a/b")
    assert result == "/a/b"


def test_integration_trailing_dotdot() -> None:
    """Test path ending with parent reference."""
    result = HttpPath.remove_dot_segments("/a/b/c/..")
    assert result == "/a/b"


def test_integration_mixed_segments() -> None:
    """Test path with mix of normal and dot segments."""
    result = HttpPath.remove_dot_segments("/a/./b/../c/./d")
    assert result == "/a/c/d"


def test_integration_empty_segments_preserved() -> None:
    """Test that empty segments (from //) are preserved."""
    result = HttpPath.remove_dot_segments("/a//b///c")
    assert result == "/a//b///c"


def test_integration_dot_in_segment_name() -> None:
    """Test that dots within segment names are preserved."""
    result = HttpPath.remove_dot_segments("/file.txt/folder.name/index.html")
    assert result == "/file.txt/folder.name/index.html"


def test_integration_multiple_consecutive_dotdots() -> None:
    """Test multiple consecutive parent references."""
    result = HttpPath.remove_dot_segments("/a/b/c/../../d")
    assert result == "/a/d"


def test_integration_dotdot_more_than_segments() -> None:
    """Test more parent references than available segments."""
    result = HttpPath.remove_dot_segments("/a/../../../b")
    assert result == "/b"


# Edge cases
def test_edge_case_single_slash() -> None:
    """Test normalizing single slash."""
    result = HttpPath.remove_dot_segments("/")
    assert result == "/"


def test_edge_case_single_dot() -> None:
    """Test normalizing single dot."""
    result = HttpPath.remove_dot_segments(".")
    # Single dot is handled specially - it's removed
    assert result == ""


def test_edge_case_single_dotdot() -> None:
    """Test normalizing single dotdot."""
    result = HttpPath.remove_dot_segments("..")
    # Single dotdot is handled specially - it's removed
    assert result == ""


def test_edge_case_no_slashes() -> None:
    """Test path with no slashes."""
    result = HttpPath.remove_dot_segments("segment")
    assert result == "segment"


def test_edge_case_relative_path_with_dots() -> None:
    """Test relative path (no leading slash) with dot segments."""
    result = HttpPath.remove_dot_segments("a/./b/../c")
    # Relative paths don't get a leading slash in the output
    assert result == "a/c"


def test_edge_case_trailing_slash_preserved() -> None:
    """Test that trailing slash in normalized path is preserved."""
    result = HttpPath.remove_dot_segments("/a/b/c/")
    assert result == "/a/b/c/"


def test_edge_case_dot_segment_creates_trailing_slash() -> None:
    """Test that removing trailing dot segment preserves slash."""
    result = HttpPath.remove_dot_segments("/a/b/./")
    assert result == "/a/b/"


# RFC 3986 Section 5.4.2 Normal Examples
def test_rfc3986_example_1() -> None:
    """RFC 3986 normal example."""
    assert HttpPath.remove_dot_segments("/a/b/c/./../../g") == "/a/g"


def test_rfc3986_example_2() -> None:
    """RFC 3986 abnormal example."""
    assert HttpPath.remove_dot_segments("mid/content=5/../6") == "mid/6"


# Performance test (stress test)
def test_stress_many_segments() -> None:
    """Test with many segments."""
    # Create a path with many segments
    path = "/a" * 100
    result = HttpPath.remove_dot_segments(path)
    assert result == path  # Should be unchanged


def test_stress_many_dot_segments() -> None:
    """Test with many dot segments."""
    # Create a path with many ./ patterns
    path = "/" + "/./".join(["a"] * 50)
    result = HttpPath.remove_dot_segments(path)
    # All ./ should be removed
    assert result == "/a/" + "/".join(["a"] * 49)
