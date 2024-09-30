"""Test the construction or URLs."""

import pytest

from utilities import assert_http_construction_expected_vs_components


@pytest.mark.parametrize(
    "expected,url_components",
    [
        (
            "http://hodor:stark@example.com",
            {"scheme": "http", "host": "example.com", "username": "hodor", "password": "stark"},
        ),
        (
            "http://hodor:stark@moo",
            {"scheme": "http", "host": "moo", "username": "hodor", "password": "stark"},
        ),
    ],
)
def test_usernames(expected: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""
    assert_http_construction_expected_vs_components(expected, url_components)
