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
        (
            "http://example.com/abc?def=ghi&jkl=mno#pqr",
            {
                "host": "example.com",
                "path": "/abc",
                "query": {"def": "ghi", "jkl": "mno"},
                "fragment": "pqr",
            },
        ),
        ("http://example.com#section1", {"host": "example.com", "fragment": "section1"}),
        (
            "http://example.com/some/path#section2",
            {
                "host": "example.com",
                "path": "/some/path",
                "fragment": "section2",
            },
        ),
    ],
)
def test_fragments(expected: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""
    assert_http_construction_expected_vs_components(expected, url_components)


def test_fragment_invalid_type() -> None:
    """Test that we can construct URLs correctly."""
    with pytest.raises(TypeError):
        url_components = {"host": "example.com", "fragment": ["foo"]}
        assert_http_construction_expected_vs_components("", url_components)


def test_fragment_property() -> None:
    """Test that reading back the property gives the same value."""
    a = HttpUrl(host="example.com", fragment="section1")
    assert a.fragment == "section1"
