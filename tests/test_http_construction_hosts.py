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
        ("http://example.com", {"host": "example.com"}),
        ("http://moo", {"host": "moo"}),
    ],
)
def test_hosts(expected: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""
    assert_http_construction_expected_vs_components(expected, url_components)


def test_host_invalid_value() -> None:
    """Test that we can construct URLs correctly."""
    with pytest.raises(TypeError):
        _ = HttpUrl(host=["foo.com"])  # type: ignore


def test_host_property() -> None:
    """Test that reading back the property gives the same value."""
    a = HttpUrl(host="example.com")
    assert a.host == "example.com"
