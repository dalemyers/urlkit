"""Test the construction or URLs."""

import os
import sys

import pytest

from utilities import assert_http_construction_expected_vs_components

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from urlkit.http_url import HttpUrl

# pylint: enable=wrong-import-position


@pytest.mark.parametrize(
    "expected,url_components",
    [
        ("http://example.com:8080", {"host": "example.com", "port": 8080}),
        ("http://moo:999", {"host": "moo", "port": 999}),
        ("http://example.com:443", {"host": "example.com", "port": 443}),
        ("http://example.com:443", {"host": "example.com", "port": "443"}),
        ("http://example.com", {"host": "example.com", "port": None}),
    ],
)
def test_ports(expected: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""
    assert_http_construction_expected_vs_components(expected, url_components)


def test_port_invalid_value() -> None:
    """Test that we can construct URLs correctly."""
    with pytest.raises(ValueError):
        url_components = {"host": "example.com", "port": "foo"}
        assert_http_construction_expected_vs_components("", url_components)


def test_port_invalid_range() -> None:
    """Test that we can construct URLs correctly."""
    with pytest.raises(ValueError):
        url_components = {"host": "example.com", "port": 100_000}
        assert_http_construction_expected_vs_components("", url_components)


def test_port_property() -> None:
    """Test that reading back the property gives the same value."""
    a = HttpUrl(host="example.com", port=9326)
    assert a.port == 9326
