"""Test the construction or URLs."""

import os
import sys

import pytest

from utilities import assert_http_construction_expected_vs_components

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from urlkit.http import HttpUrl
from urlkit.http.http_url import _parse_http_or_https_url

# pylint: enable=wrong-import-position


@pytest.mark.parametrize(
    "expected,url_components",
    [
        (
            "http://example.com/abc?def=ghi&jkl=mno#pqr",
            {
                "scheme": "http",
                "host": "example.com",
                "path": "/abc",
                "query": {"def": "ghi", "jkl": "mno"},
                "fragment": "pqr",
            },
        ),
        (
            "http://example.com#section1",
            {"scheme": "http", "host": "example.com", "fragment": "section1"},
        ),
        (
            "http://example.com/some/path#section2",
            {
                "scheme": "http",
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
    a = HttpUrl(scheme="http", host="example.com", fragment="section1")
    assert a.fragment == "section1"


def test_empty_fragment_distinct_from_absent():
    u1 = _parse_http_or_https_url("http://example.com#")
    u2 = _parse_http_or_https_url("http://example.com")
    assert u1.fragment == ""
    assert u2.fragment is None
    assert str(u1).endswith("#")
