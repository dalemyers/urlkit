"""Test the construction or URLs."""

import pytest

from utilities import assert_http_construction_expected_vs_components


@pytest.mark.parametrize(
    "expected,url_components",
    [
        ("http://example.com", {"host": "example.com", "password": "hodor"}),
        ("http://moo", {"host": "moo", "password": "hodor"}),
    ],
)
def test_only_passwords(expected: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""
    assert_http_construction_expected_vs_components(expected, url_components)
