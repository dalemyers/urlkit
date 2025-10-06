"""Test the encoding of path components."""

import pytest

from utilities import assert_http_construction_expected_vs_components


@pytest.mark.parametrize(
    "expected,url_components",
    [
        (
            "http://example.com/p%20ath",
            {"scheme": "http", "host": "example.com", "path": "/p ath"},
        ),
        (
            "http://example.com/p%3Fath",
            {"scheme": "http", "host": "example.com", "path": "/p?ath"},
        ),
        (
            "http://example.com/p%23ath",
            {"scheme": "http", "host": "example.com", "path": "/p#ath"},
        ),
        (
            "http://example.com/%E2%9C%93",
            {"scheme": "http", "host": "example.com", "path": "/✓"},
        ),
    ],
)
def test_path_construction_encoding(expected: str, url_components: dict) -> None:
    """Test that path components are properly percent-encoded during construction."""
    assert_http_construction_expected_vs_components(expected, url_components)
