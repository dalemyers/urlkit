"""Test the construction or URLs."""

import pytest

from utilities import assert_http_construction_expected_vs_components


@pytest.mark.parametrize(
    "expected,url_components",
    [
        (
            "http:/a/path/here",
            {"scheme": "http", "host": None, "path": "a/path/here"},
        ),  # Not according to spec, but covers 99.999999% of use cases
        ("http:/a/path/here", {"scheme": "http", "host": None, "path": "/a/path/here"}),
    ],
)
def test_netloc(expected: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""
    assert_http_construction_expected_vs_components(expected, url_components)
