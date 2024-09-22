"""Test the construction or URLs."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from urlkit.http_url import BaseHttpOrHttpsUrl, HttpsUrl, HttpUrl
from urlkit.http_queries import QueryOptions, SpaceEncoding

# pylint: enable=wrong-import-position


def test_scheme_invalid_value() -> None:
    """Test that we can construct URLs correctly."""
    with pytest.raises(ValueError):
        _ = BaseHttpOrHttpsUrl(scheme="hodor", host="example.com")


def test_schemeproperty() -> None:
    """Test that reading back the property gives the same value."""
    a = BaseHttpOrHttpsUrl(host="example.com", scheme="https")
    assert a.scheme == "https"
    a.scheme = "http"
    assert a.scheme == "http"


def test_repr() -> None:
    """Test that we can construct URLs correctly."""
    assert (
        repr(BaseHttpOrHttpsUrl(scheme="https", host="example.com"))
        == "BaseHttpOrHttpsUrl(https://example.com)"
    )
    assert repr(HttpsUrl(host="example.com")) == "HttpsUrl(https://example.com)"
    assert repr(HttpUrl(host="example.com")) == "HttpUrl(http://example.com)"


def test_eq() -> None:
    """Test that we can construct URLs correctly."""
    assert BaseHttpOrHttpsUrl(scheme="https", host="example.com") == BaseHttpOrHttpsUrl(
        scheme="https", host="example.com"
    )
    assert BaseHttpOrHttpsUrl(
        scheme="https",
        host="example.com",
        username="hello",
        password="world",
        port=12345,
        path="/some/path",
        query={"one": "1", "two": "2"},
        fragment="fragment",
        query_options=QueryOptions(
            query_joiner="^",
            safe_characters="!",
            space_encoding=SpaceEncoding.PLUS,
        ),
    ) == BaseHttpOrHttpsUrl(
        scheme="https",
        host="example.com",
        username="hello",
        password="world",
        port=12345,
        path="/some/path",
        query={"one": "1", "two": "2"},
        fragment="fragment",
        query_options=QueryOptions(
            query_joiner="^",
            safe_characters="!",
            space_encoding=SpaceEncoding.PLUS,
        ),
    )
    assert BaseHttpOrHttpsUrl(scheme="https", host="example.com") != BaseHttpOrHttpsUrl(
        scheme="http", host="example.com"
    )

    assert BaseHttpOrHttpsUrl(scheme="https", host="example.com") != 12345


def test_hash() -> None:
    """Test that we can construct URLs correctly."""
    assert hash(BaseHttpOrHttpsUrl(scheme="https", host="example.com")) == hash(
        BaseHttpOrHttpsUrl(scheme="https", host="example.com")
    )
    assert hash(
        BaseHttpOrHttpsUrl(
            scheme="https",
            host="example.com",
            username="hello",
            password="world",
            port=12345,
            path="/some/path",
            query={"one": "1", "two": "2"},
            fragment="fragment",
            query_options=QueryOptions(
                query_joiner="^",
                safe_characters="!",
                space_encoding=SpaceEncoding.PLUS,
            ),
        )
    ) == hash(
        BaseHttpOrHttpsUrl(
            scheme="https",
            host="example.com",
            username="hello",
            password="world",
            port=12345,
            path="/some/path",
            query={"one": "1", "two": "2"},
            fragment="fragment",
            query_options=QueryOptions(
                query_joiner="^",
                safe_characters="!",
                space_encoding=SpaceEncoding.PLUS,
            ),
        )
    )

    assert hash(BaseHttpOrHttpsUrl(scheme="https", host="example.com")) != hash(
        BaseHttpOrHttpsUrl(scheme="http", host="example.com")
    )

    assert hash(
        BaseHttpOrHttpsUrl(scheme="https", host="example.com", query={"one": "1", "two": "2"})
    ) == hash(
        BaseHttpOrHttpsUrl(scheme="https", host="example.com", query={"two": "2", "one": "1"})
    )
