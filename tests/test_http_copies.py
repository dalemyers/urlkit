"""Test the construction or URLs."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from urlkit import HttpUrl
from urlkit.http import QueryOptions

# pylint: enable=wrong-import-position


def test_copies() -> None:
    """Test that we can construct URLs correctly."""
    a = HttpUrl(
        scheme="http",
        host="example.com",
        port=9326,
        username="hodor",
        password="stark",
        path="/some/path",
        query={"foo": "bar"},
        fragment="section1",
        parameters="a;b",
        query_options=QueryOptions(),
    )

    b = a.copy()
    b.scheme = "https"
    assert a.scheme == "http"

    c = a.copy()
    c.host = "example.org"
    assert a.host == "example.com"

    d = a.copy()
    d.port = 1234
    assert a.port == 9326

    e = a.copy()
    e.username = "hello"
    assert a.username == "hodor"

    f = a.copy()
    f.password = "world"
    assert a.password == "stark"

    g = a.copy()
    g.path = "/another/path"
    assert str(a.path) == "/some/path"

    h = a.copy()
    h.path.append("another")
    assert str(a.path) == "/some/path"

    i = a.copy()
    i.query["foo"] = "baz"
    assert a.query["foo"].value == "bar"

    j = a.copy()
    j.query["bar"] = "baz"
    assert "bar" not in a.query

    k = a.copy()
    k.fragment = "section2"
    assert a.fragment == "section1"

    l = a.copy()
    l.parameters = "c;d"
    assert a.parameters == "a;b"

    m = a.copy()
    m.query_options = QueryOptions(query_joiner="*")
    assert a.query_options == QueryOptions()
