"""Test the construction or URLs."""

import pytest

from utilities import assert_http_construction_expected_vs_components


@pytest.mark.parametrize(
    "expected,url_components",
    [
        ("http:a/path/here", {"host": None, "path": "a/path/here"}),
        ("http:/a/path/here", {"host": None, "path": "/a/path/here"}),
    ],
)
def test_netloc(expected: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""
    assert_http_construction_expected_vs_components(expected, url_components)
