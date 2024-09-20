"""Test the construction or URLs."""

import os
import sys

import pytest

from utilities import assert_http_expected_vs_components

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from urlkit.http_url import BaseHttpOrHttpsUrl, HttpsUrl, HttpUrl

# pylint: enable=wrong-import-position


def test_scheme_invalid_value() -> None:
    """Test that we can construct URLs correctly."""
    with pytest.raises(ValueError):
        _ = BaseHttpOrHttpsUrl(scheme="hodor", host="example.com")


def test_repr() -> None:
    """Test that we can construct URLs correctly."""
    assert (
        repr(BaseHttpOrHttpsUrl(scheme="https", host="example.com"))
        == "BaseHttpOrHttpsUrl(https://example.com)"
    )
    assert repr(HttpsUrl(host="example.com")) == "HttpsUrl(https://example.com)"
    assert repr(HttpUrl(host="example.com")) == "HttpUrl(http://example.com)"
