"""Tests for the netloc parsing helper functions."""

import pytest

from urlkit.http.http_url import (
    _split_userinfo_from_netloc,
    _parse_userinfo,
    _parse_ipv6_host_and_port,
    _parse_host_and_port,
)


# _split_userinfo_from_netloc tests
def test_split_userinfo_with_userinfo() -> None:
    """Test splitting netloc with userinfo present."""
    userinfo, host_and_port = _split_userinfo_from_netloc("user:pass@example.com:8080")

    assert userinfo == "user:pass"
    assert host_and_port == "example.com:8080"


def test_split_userinfo_without_userinfo() -> None:
    """Test splitting netloc without userinfo."""
    userinfo, host_and_port = _split_userinfo_from_netloc("example.com:8080")

    assert userinfo is None
    assert host_and_port == "example.com:8080"


def test_split_userinfo_username_only() -> None:
    """Test splitting netloc with username but no password."""
    userinfo, host_and_port = _split_userinfo_from_netloc("user@example.com")

    assert userinfo == "user"
    assert host_and_port == "example.com"


def test_split_userinfo_with_ipv6() -> None:
    """Test splitting netloc with IPv6 address."""
    userinfo, host_and_port = _split_userinfo_from_netloc("user@[::1]:8080")

    assert userinfo == "user"
    assert host_and_port == "[::1]:8080"


def test_split_userinfo_multiple_at_signs() -> None:
    """Test splitting with multiple @ signs (only first is separator)."""
    userinfo, host_and_port = _split_userinfo_from_netloc("user@domain@example.com")

    assert userinfo == "user"
    assert host_and_port == "domain@example.com"


# _parse_userinfo tests
def test_parse_userinfo_with_password() -> None:
    """Test parsing userinfo with username and password."""
    username, password = _parse_userinfo("user:pass")

    assert username == "user"
    assert password == "pass"


def test_parse_userinfo_without_password() -> None:
    """Test parsing userinfo with username only."""
    username, password = _parse_userinfo("user")

    assert username == "user"
    assert password is None


def test_parse_userinfo_none() -> None:
    """Test parsing None userinfo."""
    username, password = _parse_userinfo(None)

    assert username is None
    assert password is None


def test_parse_userinfo_empty_string() -> None:
    """Test parsing empty userinfo string."""
    username, password = _parse_userinfo("")

    assert username is None
    assert password is None


def test_parse_userinfo_password_with_colons() -> None:
    """Test parsing userinfo where password contains colons."""
    username, password = _parse_userinfo("user:pass:word:with:colons")

    assert username == "user"
    assert password == "pass:word:with:colons"


def test_parse_userinfo_empty_password() -> None:
    """Test parsing userinfo with empty password."""
    username, password = _parse_userinfo("user:")

    assert username == "user"
    assert password == ""


# _parse_ipv6_host_and_port tests
def test_parse_ipv6_basic() -> None:
    """Test parsing basic IPv6 address."""
    host, port = _parse_ipv6_host_and_port("[::1]")

    assert host == "[::1]"
    assert port is None


def test_parse_ipv6_with_port() -> None:
    """Test parsing IPv6 address with port."""
    host, port = _parse_ipv6_host_and_port("[::1]:8080")

    assert host == "[::1]"
    assert port == 8080


def test_parse_ipv6_full_address() -> None:
    """Test parsing full IPv6 address."""
    host, port = _parse_ipv6_host_and_port("[2001:0db8:85a3:0000:0000:8a2e:0370:7334]:443")

    assert host == "[2001:0db8:85a3:0000:0000:8a2e:0370:7334]"
    assert port == 443


def test_parse_ipv6_localhost() -> None:
    """Test parsing IPv6 localhost."""
    host, port = _parse_ipv6_host_and_port("[::ffff:127.0.0.1]:9000")

    assert host == "[::ffff:127.0.0.1]"
    assert port == 9000


def test_parse_ipv6_empty_port() -> None:
    """Test parsing IPv6 with colon but empty port."""
    host, port = _parse_ipv6_host_and_port("[::1]:")

    assert host == "[::1]"
    assert port is None


def test_parse_ipv6_missing_closing_bracket() -> None:
    """Test parsing IPv6 with missing closing bracket raises error."""
    with pytest.raises(ValueError) as exc_info:
        _parse_ipv6_host_and_port("[::1")

    assert "missing closing ']'" in str(exc_info.value)


def test_parse_ipv6_unexpected_chars_after_bracket() -> None:
    """Test parsing IPv6 with unexpected characters after bracket."""
    with pytest.raises(ValueError) as exc_info:
        _parse_ipv6_host_and_port("[::1]abc")

    assert "unexpected characters after ']'" in str(exc_info.value)


# _parse_host_and_port tests
def test_parse_host_and_port_simple_host() -> None:
    """Test parsing simple hostname without port."""
    host, port = _parse_host_and_port("example.com")

    assert host == "example.com"
    assert port is None


def test_parse_host_and_port_with_port() -> None:
    """Test parsing hostname with port."""
    host, port = _parse_host_and_port("example.com:8080")

    assert host == "example.com"
    assert port == 8080


def test_parse_host_and_port_ipv4() -> None:
    """Test parsing IPv4 address."""
    host, port = _parse_host_and_port("192.168.1.1:3000")

    assert host == "192.168.1.1"
    assert port == 3000


def test_parse_host_and_port_empty_port() -> None:
    """Test parsing host with colon but empty port."""
    host, port = _parse_host_and_port("example.com:")

    assert host == "example.com"
    assert port is None


def test_parse_host_and_port_ipv6_delegates() -> None:
    """Test that IPv6 addresses delegate to _parse_ipv6_host_and_port."""
    host, port = _parse_host_and_port("[::1]:8080")

    assert host == "[::1]"
    assert port == 8080


def test_parse_host_and_port_multiple_colons_uses_last() -> None:
    """Test that with multiple colons, the last one is used for port."""
    # This shouldn't happen in practice with valid hostnames, but tests the logic
    host, port = _parse_host_and_port("host:with:colons:9000")

    assert host == "host:with:colons"
    assert port == 9000


def test_parse_host_and_port_localhost() -> None:
    """Test parsing localhost."""
    host, port = _parse_host_and_port("localhost:3000")

    assert host == "localhost"
    assert port == 3000


def test_parse_host_and_port_subdomain() -> None:
    """Test parsing hostname with subdomains."""
    host, port = _parse_host_and_port("api.v1.example.com:443")

    assert host == "api.v1.example.com"
    assert port == 443


# Integration tests
def test_ipv6_integration_no_port() -> None:
    """Integration test for IPv6 without port."""
    host, port = _parse_host_and_port("[2001:db8::1]")

    assert host == "[2001:db8::1]"
    assert port is None


def test_ipv6_integration_with_port() -> None:
    """Integration test for IPv6 with port."""
    host, port = _parse_host_and_port("[2001:db8::1]:443")

    assert host == "[2001:db8::1]"
    assert port == 443


def test_edge_case_numeric_hostname() -> None:
    """Test parsing numeric-looking hostname."""
    host, port = _parse_host_and_port("123:456")

    assert host == "123"
    assert port == 456


def test_edge_case_single_char_host() -> None:
    """Test parsing single character hostname."""
    host, port = _parse_host_and_port("a:80")

    assert host == "a"
    assert port == 80
