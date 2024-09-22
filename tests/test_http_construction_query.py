"""Test the construction or URLs."""

import os
import sys

import pytest

from utilities import assert_http_construction_expected_vs_components

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from urlkit.http_queries import QueryOptions, SpaceEncoding
from urlkit.http_url import HttpUrl

# pylint: enable=wrong-import-position


@pytest.mark.parametrize(
    "expected,url_components",
    [
        (
            "http://example.com/?def=ghi",
            {"host": "example.com", "query": "def=ghi"},
        ),
        (
            "http://example.com/?def=ghi",
            {"host": "example.com", "query": {"def": "ghi"}},
        ),
        (
            "http://example.com/?def=ghi&jkl=mno",
            {"host": "example.com", "query": {"def": "ghi", "jkl": "mno"}},
        ),
        (
            "http://localhost/?a&b&a%26b",
            {
                "host": "localhost",
                "query": "a&b&a%26b",
            },
        ),
        ("http://example.com/?name=alice", {"host": "example.com", "query": {"name": "alice"}}),
        (
            "http://example.com/?name=alice&age=30",
            {"host": "example.com", "query": {"name": "alice", "age": 30}},
        ),
        (
            "http://example.com/?search=python",
            {"host": "example.com", "query": "search=python"},
        ),
        # Very large query strings
        (
            "http://example.com/?param1=val1&param2=val2&param3=val3&param4=val4&param5=val5&param6=val6&param7=val7&param8=val8",
            {
                "host": "example.com",
                "query": {
                    "param1": "val1",
                    "param2": "val2",
                    "param3": "val3",
                    "param4": "val4",
                    "param5": "val5",
                    "param6": "val6",
                    "param7": "val7",
                    "param8": "val8",
                },
            },
        ),
    ],
)
def test_query_parameters_simple(expected: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""
    assert_http_construction_expected_vs_components(expected, url_components)


@pytest.mark.parametrize(
    "expected,url_components",
    [
        # Query string with booleans and numbers
        (
            "http://example.com/?enabled=true&count=10",
            {"host": "example.com", "query": {"enabled": True, "count": 10}},
        ),
        # Query string with mixed types
        (
            "http://example.com/?bool=true&int=42&float=3.14&str=hello",
            {
                "host": "example.com",
                "query": {"bool": "true", "int": 42, "float": 3.14, "str": "hello"},
            },
        ),
        # Query string with empty values and None
        (
            "http://example.com/?empty=&none",
            {"host": "example.com", "query": {"empty": "", "none": None}},
        ),  # Encodes None as a key without value
        # Mixed pre-encoded and non-encoded queries
        (
            "http://example.com/?category=electronics&query=search%20results&page=2",
            {
                "host": "example.com",
                "query": {"category": "electronics", "query": "search results", "page": "2"},
            },
        ),
    ],
)
def test_query_parameters_types(expected: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""
    assert_http_construction_expected_vs_components(expected, url_components)


@pytest.mark.parametrize(
    "expected,url_components",
    [
        # Query string with special characters
        (
            "http://example.com/report?text=%23Report%202023%20Update&year=2023",
            {
                "host": "example.com",
                "path": "/report",
                "query": {"text": "#Report 2023 Update", "year": "2023"},
            },
        ),
        (
            "http://example.com/?search=hello%20world",
            {"host": "example.com", "query": "search=hello%20world"},
        ),
        # Special characters in query strings (percent-encoded)
        (
            "http://example.com/?query=%40username%21%24%25%5E&email=user%40example.com",
            {
                "host": "example.com",
                "query": {"query": "@username!$%^", "email": "user@example.com"},
            },
        ),
        (
            "http://example.com/?query=%3Cscript%3Ealert%281%29%3C%2Fscript%3E",
            {"host": "example.com", "query": {"query": "<script>alert(1)</script>"}},
        ),  # Encodes HTML/JS characters
        # Query string with international characters (encoded as UTF-8)
        (
            "http://example.com/?search=%C3%A9l%C3%A9phant&lang=fr",
            {"host": "example.com", "query": {"search": "éléphant", "lang": "fr"}},
        ),  # Encoded UTF-8 for accented characters
        (
            "http://example.com/?greeting=%E6%97%A5%E6%9C%AC%E8%AA%9E",
            {"host": "example.com", "query": {"greeting": "日本語"}},
        ),  # Japanese characters
        # Query string with special symbols
        (
            "http://example.com/?query=%3C%3E%26%23%25",
            {"host": "example.com", "query": {"query": "<>&#%"}},
        ),  # Encodes <, >, &, #, %
        (
            "http://example.com/?password=%40dm1n%24ecure%21",
            {"host": "example.com", "query": {"password": "@dm1n$ecure!"}},
        ),  # Encodes special characters in passwords
        # Pre-encoded query string with nested parameters
        (
            "http://example.com/?filter%5Bcategory%5D=electronics&filter%5Bprice%5D%5Bmin%5D=20&filter%5Bprice%5D%5Bmax%5D=500",
            {
                "host": "example.com",
                "query": "filter%5Bcategory%5D=electronics&filter%5Bprice%5D%5Bmin%5D=20&filter%5Bprice%5D%5Bmax%5D=500",
            },
        ),
    ],
)
def test_query_parameters_base_encoding(expected: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""
    assert_http_construction_expected_vs_components(expected, url_components)


@pytest.mark.parametrize(
    "expected,url_components",
    [
        (
            "http://example.com/?foo=bar",
            {
                "host": "example.com",
                "query": {"foo": "bar"},
                "query_options": QueryOptions(),
            },
        ),
        (
            "http://example.com/?foo=bar<>baz=qux",
            {
                "host": "example.com",
                "query": {"foo": "bar", "baz": "qux"},
                "query_options": QueryOptions(query_joiner="<>"),
            },
        ),
        (
            "http://example.com/?foo=/bar/baz",
            {
                "host": "example.com",
                "query": {"foo": "/bar/baz"},
                "query_options": QueryOptions(safe_characters="/"),
            },
        ),
        (
            "http://example.com/?foo=bar%20baz",
            {
                "host": "example.com",
                "query": {"foo": "bar baz"},
                "query_options": QueryOptions(space_encoding=SpaceEncoding.PERCENT),
            },
        ),
        (
            "http://example.com/?foo=bar+baz",
            {
                "host": "example.com",
                "query": {"foo": "bar baz"},
                "query_options": QueryOptions(space_encoding=SpaceEncoding.PLUS),
            },
        ),
        (
            "http://example.com/?foo=bar+baz",
            {
                "host": "example.com",
                "query": "foo=bar baz",
                "query_options": QueryOptions(space_encoding=SpaceEncoding.PLUS),
            },
        ),
    ],
)
def test_query_parameters_custom_encoding(expected: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""
    assert_http_construction_expected_vs_components(expected, url_components)


def test_query_parameters_invalid_space_encoding() -> None:
    """Test that we can construct URLs correctly."""
    with pytest.raises(ValueError):
        url_components = {
            "host": "example.com",
            "query": {"foo": "bar"},
            "query_options": QueryOptions(space_encoding="INVALID"),  # type: ignore
        }
        assert_http_construction_expected_vs_components("", url_components)

    with pytest.raises(ValueError):
        url_components = {
            "host": "example.com",
            "query": "foo=bar",
            "query_options": QueryOptions(space_encoding="INVALID"),  # type: ignore
        }
        assert_http_construction_expected_vs_components("", url_components)


def test_query_parameters_invalid_query_options_value() -> None:
    """Test that we can construct URLs correctly."""
    with pytest.raises(TypeError):
        url_components = {
            "host": "example.com",
            "query": {"foo": "bar"},
            "query_options": object(),  # type: ignore
        }
        assert_http_construction_expected_vs_components("", url_components)


def test_query_parameters_invalid_value_type() -> None:
    """Test that we can construct URLs correctly."""
    with pytest.raises(ValueError):
        url_components = {
            "host": "example.com",
            "query": {"foo": object()},
        }
        assert_http_construction_expected_vs_components("", url_components)


def test_query_parameters_invalid_type() -> None:
    """Test that we can construct URLs correctly."""
    with pytest.raises(TypeError):
        url_components = {"host": "example.com", "query": ["foo"]}
        assert_http_construction_expected_vs_components("", url_components)


def test_query_property() -> None:
    """Test that reading back the property gives the same value."""
    a = HttpUrl(host="example.com", query={"one": "1", "two": "2"})
    assert a.query == {"one": "1", "two": "2"}


def test_query_options_property() -> None:
    """Test that reading back the property gives the same value."""
    options = QueryOptions(query_joiner="|")
    a = HttpUrl(host="example.com", query_options=options)
    assert a.query_options == options


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (
            QueryOptions(),
            QueryOptions(),
            True,
        ),
        (
            QueryOptions(),
            4,
            False,
        ),
        (
            QueryOptions(),
            QueryOptions(query_joiner="|"),
            False,
        ),
        (
            QueryOptions(
                query_joiner="|",
                safe_characters="/",
                space_encoding=SpaceEncoding.PLUS,
            ),
            QueryOptions(
                query_joiner="|",
                safe_characters="/",
                space_encoding=SpaceEncoding.PLUS,
            ),
            True,
        ),
        (
            QueryOptions(
                query_joiner="|",
                safe_characters="/",
                space_encoding=SpaceEncoding.PLUS,
            ),
            QueryOptions(
                query_joiner="|",
                safe_characters="/",
                space_encoding=SpaceEncoding.PERCENT,
            ),
            False,
        ),
    ],
)
def test_query_options_equality(a: QueryOptions, b: QueryOptions, expected: bool) -> None:
    """Test that reading back the property gives the same value."""
    assert (a == b) is expected
