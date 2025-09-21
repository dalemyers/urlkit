"""Test the construction or URLs."""

import os
import sys

import pytest

from utilities import assert_http_construction_expected_vs_components

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from urlkit.http import HttpUrl

# pylint: enable=wrong-import-position


@pytest.mark.parametrize(
    "expected,url_components",
    [
        ("http://example.com", {"scheme": "http", "host": "example.com"}),
        ("http://moo", {"scheme": "http", "host": "moo"}),
        ("http://127.0.0.1", {"scheme": "http", "host": "127.0.0.1"}),
        ("http://[::1]", {"scheme": "http", "host": "[::1]"}),
        ("http://[2001:db8::1]", {"scheme": "http", "host": "[2001:db8::1]"}),
        ("http://example.com", {"scheme": "http", "host": "EXAMPLE.com"}),
        (
            "http://example.com",
            {
                "scheme": "HTTP",  # Technically a scheme test but we don't have a specific file for that
                "host": "EXAMPLE.com",
            },
        ),
    ],
)
def test_hosts(expected: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""
    assert_http_construction_expected_vs_components(expected, url_components)


def test_host_invalid_value() -> None:
    """Test that we can construct URLs correctly."""
    with pytest.raises(TypeError):
        _ = HttpUrl(scheme="http", host=["foo.com"])  # type: ignore


def test_host_property() -> None:
    """Test that reading back the property gives the same value."""
    a = HttpUrl(scheme="http", host="example.com")
    assert a.host == "example.com"
