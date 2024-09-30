"""Test the construction or URLs."""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from urlkit.http.http_url import HttpUrl
from urlkit.http.http_queries import QueryOptions, SpaceEncoding, QuerySet

# pylint: enable=wrong-import-position


def test_scheme_invalid_value() -> None:
    """Test that we can construct URLs correctly."""
    with pytest.raises(ValueError):
        _ = HttpUrl(scheme="hodor", host="example.com")


def test_schemeproperty() -> None:
    """Test that reading back the property gives the same value."""
    a = HttpUrl(host="example.com", scheme="https")
    assert a.scheme == "https"
    a.scheme = "http"
    assert a.scheme == "http"


def test_repr() -> None:
    """Test that we can construct URLs correctly."""
    assert repr(HttpUrl(scheme="https", host="example.com")) == "HttpUrl(https://example.com)"
    assert repr(HttpUrl(scheme="https", host="example.com")) == "HttpUrl(https://example.com)"
    assert repr(HttpUrl(scheme="http", host="example.com")) == "HttpUrl(http://example.com)"


def test_eq() -> None:
    """Test that we can construct URLs correctly."""
    assert HttpUrl(scheme="https", host="example.com") == HttpUrl(
        scheme="https", host="example.com"
    )
    query_options = QueryOptions(
        query_joiner="^",
        safe_characters="!",
        space_encoding=SpaceEncoding.PLUS,
    )
    query_set = QuerySet(query_options)
    query_set["one"] = "1"
    query_set["two"] = "2"

    assert HttpUrl(
        scheme="https",
        host="example.com",
        username="hello",
        password="world",
        port=12345,
        path="/some/path",
        query={"one": "1", "two": "2"},
        fragment="fragment",
        query_options=query_options,
    ) == HttpUrl(
        scheme="https",
        host="example.com",
        username="hello",
        password="world",
        port=12345,
        path="/some/path",
        query=query_set,
        fragment="fragment",
        query_options=query_options,
    )
    assert HttpUrl(scheme="https", host="example.com") != HttpUrl(scheme="http", host="example.com")

    assert HttpUrl(scheme="https", host="example.com") != 12345


def test_hash() -> None:
    """Test that we can construct URLs correctly."""
    assert hash(HttpUrl(scheme="https", host="example.com")) == hash(
        HttpUrl(scheme="https", host="example.com")
    )
    assert hash(
        HttpUrl(
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
        HttpUrl(
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

    assert hash(HttpUrl(scheme="https", host="example.com")) != hash(
        HttpUrl(scheme="http", host="example.com")
    )

    assert hash(
        HttpUrl(scheme="https", host="example.com", query={"one": "1", "two": "2"})
    ) == hash(HttpUrl(scheme="https", host="example.com", query={"two": "2", "one": "1"}))
