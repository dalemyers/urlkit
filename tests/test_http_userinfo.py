'''Test the construction and parsing of userinfo in URLs.'''

import pytest

from utilities import assert_http_construction_expected_vs_components
from urlkit.http import HttpUrl


@pytest.mark.parametrize(
    "url,expected_username,expected_password",
    [
        ("http://user%20name@example.com", "user name", None),
        ("http://user%40name@example.com", "user@name", None),
        ("http://user:p%40ssword@example.com", "user", "p@ssword"),
        ("http://user:p%2Fssword@example.com", "user", "p/ssword"),
        ("http://user:p%3Assword@example.com", "user", "p:ssword"),
        ("http://%25user%25:%25pass%25@example.com", "%user%", "%pass%"),
    ],
)
def test_userinfo_parsing_percent_encoded(url: str, expected_username: str, expected_password: str | None) -> None:
    '''Test that percent-encoded characters in userinfo are properly decoded during parsing.'''
    # This test expects that the library correctly decodes userinfo, which is required by spec.
    # The current implementation does not, so this test will fail and highlight the gap.
    parsed_url = HttpUrl.parse(url)
    assert parsed_url.username == expected_username
    assert parsed_url.password == expected_password


@pytest.mark.parametrize(
    "expected,url_components",
    [
        (
            "http://user%20name@example.com",
            {"scheme": "http", "host": "example.com", "username": "user name"},
        ),
        (
            "http://user%40name@example.com",
            {"scheme": "http", "host": "example.com", "username": "user@name"},
        ),
        (
            "http://user:p%40ssword@example.com",
            {"scheme": "http", "host": "example.com", "username": "user", "password": "p@ssword"},
        ),
        (
            "http://user:p%2Fssword@example.com",
            {"scheme": "http", "host": "example.com", "username": "user", "password": "p/ssword"},
        ),
        (
            "http://user:p%3Assword@example.com",
            {"scheme": "http", "host": "example.com", "username": "user", "password": "p:ssword"},
        ),
    ],
)
def test_userinfo_construction_percent_encoding(expected: str, url_components: dict) -> None:
    '''Test that userinfo components are properly percent-encoded during construction.'''
    # This test expects that the library correctly encodes userinfo, which is required by spec.
    # The current implementation does not, so this test will fail and highlight the gap.
    assert_http_construction_expected_vs_components(expected, url_components)