"""Test HttpUrl equality and hashing behavior."""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from urlkit.http import HttpUrl, QueryOptions, QuerySet, HttpPath

# pylint: enable=wrong-import-position


def test_http_url_basic_equality() -> None:
    """Identical component sets compare equal."""
    a = HttpUrl(scheme="http", host="example.com", path="/foo", query={"a": "1"}, fragment="frag")
    b = HttpUrl(scheme="http", host="example.com", path="/foo", query={"a": "1"}, fragment="frag")
    assert a == b
    assert hash(a) == hash(b)


@pytest.mark.parametrize(
    "a_kwargs,b_kwargs,different_field",
    [
        (
            {"scheme": "http", "host": "example.com"},
            {"scheme": "https", "host": "example.com"},
            "scheme",
        ),
        (
            {"scheme": "http", "host": "example.com"},
            {"scheme": "http", "host": "example.org"},
            "host",
        ),
        (
            {"scheme": "http", "host": "example.com", "port": 80},
            {"scheme": "http", "host": "example.com", "port": 8080},
            "port",
        ),
        (
            {"scheme": "http", "host": "example.com", "path": "/one"},
            {"scheme": "http", "host": "example.com", "path": "/two"},
            "path",
        ),
        (
            {"scheme": "http", "host": "example.com", "query": {"a": "1"}},
            {"scheme": "http", "host": "example.com", "query": {"a": "2"}},
            "query-value",
        ),
        (
            {"scheme": "http", "host": "example.com", "query": {"a": "1"}},
            {"scheme": "http", "host": "example.com", "query": {"b": "1"}},
            "query-key",
        ),
        (
            {"scheme": "http", "host": "example.com", "fragment": "top"},
            {"scheme": "http", "host": "example.com", "fragment": "bottom"},
            "fragment",
        ),
        (
            {
                "scheme": "http",
                "host": "example.com",
                "query": {"a": "1"},
                "query_options": QueryOptions(query_joiner="&"),
            },
            {
                "scheme": "http",
                "host": "example.com",
                "query": {"a": "1"},
                "query_options": QueryOptions(query_joiner="|"),
            },
            "query_options",
        ),
    ],
)
def test_http_url_inequality(a_kwargs: dict, b_kwargs: dict, different_field: str) -> None:
    """Different critical components should yield inequality."""
    a = HttpUrl(**a_kwargs)
    b = HttpUrl(**b_kwargs)
    assert a != b, f"Expected inequality when differing in {different_field}"


def test_http_url_query_equivalence_with_different_insertion_order() -> None:
    """Dict insertion order differences should not affect equality."""
    a = HttpUrl(scheme="http", host="example.com", query={"a": "1", "b": "2"})
    q = QuerySet(QueryOptions())
    q["b"] = "2"
    q["a"] = "1"
    b = HttpUrl(scheme="http", host="example.com", query=q)
    assert a == b


def test_http_url_path_object_vs_string() -> None:
    """Supplying path as string vs equivalent components should compare equal."""
    a = HttpUrl(scheme="http", host="example.com", path="/alpha/beta")
    b = HttpUrl(scheme="http", host="example.com", path=HttpPath("/alpha/beta"))
    assert a == b


def test_http_url_inequality_username() -> None:
    """Different username should affect equality (desired future behavior)."""
    a = HttpUrl(scheme="http", host="example.com", username="alice")
    b = HttpUrl(scheme="http", host="example.com", username="bob")
    assert a != b


def test_http_url_inequality_password() -> None:
    """Different password should affect equality (desired future behavior)."""
    a = HttpUrl(scheme="http", host="example.com", username="alice", password="secret")
    b = HttpUrl(scheme="http", host="example.com", username="alice", password="other")
    assert a != b


def test_http_url_port_string_int_equivalence() -> None:
    """Equivalent numeric port values (string vs int) should compare equal after normalization."""
    a = HttpUrl(scheme="http", host="example.com", port=80)
    b = HttpUrl(scheme="http", host="example.com", port="80")  # type: ignore[arg-type]
    assert a == b


def test_http_url_hash_consistency_across_recreation() -> None:
    """Recreating identical URL should yield same hash (hash depends only on compared fields)."""
    a = HttpUrl(scheme="https", host="example.com", path="/p", query={"q": "1"}, fragment="frag")
    b = HttpUrl(scheme="https", host="example.com", path="/p", query={"q": "1"}, fragment="frag")
    assert a == b
    assert hash(a) == hash(b)


def test_http_url_hash_difference_when_component_differs() -> None:
    """Change in a compared component should change hash (very high probability)."""
    a = HttpUrl(scheme="http", host="example.com", query={"k": "1"})
    b = HttpUrl(scheme="http", host="example.com", query={"k": "2"})
    assert a != b
    assert hash(a) != hash(b)
