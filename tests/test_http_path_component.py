"""Test the HttpPathComponent class."""

import copy

import pytest

from urlkit.http.http_path import HttpPathComponent


def test_http_path_component_basic_creation() -> None:
    """Test creating basic HttpPathComponent objects."""
    component = HttpPathComponent("test", False)
    assert component.value == "test"
    assert component.encoded is False

    component_encoded = HttpPathComponent("test%20value", True)
    assert component_encoded.value == "test%20value"
    assert component_encoded.encoded is True


def test_http_path_component_equality_unencoded() -> None:
    """Test equality of unencoded HttpPathComponent objects."""
    comp1 = HttpPathComponent("hello", False)
    comp2 = HttpPathComponent("hello", False)
    comp3 = HttpPathComponent("world", False)

    assert comp1 == comp2
    assert comp1 != comp3


def test_http_path_component_equality_encoded() -> None:
    """Test equality of encoded HttpPathComponent objects."""
    comp1 = HttpPathComponent("hello%20world", True)
    comp2 = HttpPathComponent("hello%20world", True)
    comp3 = HttpPathComponent("hello%20there", True)

    assert comp1 == comp2
    assert comp1 != comp3


def test_http_path_component_equality_mixed() -> None:
    """Test equality between encoded and unencoded components."""
    comp_unencoded = HttpPathComponent("hello world", False)
    comp_encoded = HttpPathComponent("hello%20world", True)

    assert comp_unencoded == comp_encoded


def test_http_path_component_equality_special_chars() -> None:
    """Test equality with special characters."""
    comp1 = HttpPathComponent("a?b", False)
    comp2 = HttpPathComponent("a%3Fb", True)
    assert comp1 == comp2

    comp3 = HttpPathComponent("a#b", False)
    comp4 = HttpPathComponent("a%23b", True)
    assert comp3 == comp4


def test_http_path_component_equality_non_component() -> None:
    """Test equality with non-HttpPathComponent objects."""
    comp = HttpPathComponent("test", False)
    assert comp != "test"
    assert comp != 123
    assert comp != None
    assert comp != ["test"]


def test_http_path_component_hash_unencoded() -> None:
    """Test hashing of unencoded HttpPathComponent objects."""
    comp1 = HttpPathComponent("hello", False)
    comp2 = HttpPathComponent("hello", False)

    assert hash(comp1) == hash(comp2)

    # Should be usable in sets and dicts
    component_set = {comp1, comp2}
    assert len(component_set) == 1


def test_http_path_component_hash_encoded() -> None:
    """Test hashing of encoded HttpPathComponent objects."""
    comp1 = HttpPathComponent("hello%20world", True)
    comp2 = HttpPathComponent("hello%20world", True)

    assert hash(comp1) == hash(comp2)


def test_http_path_component_hash_mixed() -> None:
    """Test hashing between encoded and unencoded components."""
    comp_unencoded = HttpPathComponent("hello world", False)
    comp_encoded = HttpPathComponent("hello%20world", True)

    # They should have the same hash since they're equal
    assert hash(comp_unencoded) == hash(comp_encoded)


def test_http_path_component_hash_in_dict() -> None:
    """Test using HttpPathComponent as dictionary keys."""
    comp1 = HttpPathComponent("key", False)
    comp2 = HttpPathComponent("key", False)
    comp3 = HttpPathComponent("other", False)

    test_dict = {comp1: "value1"}
    test_dict[comp2] = "value2"
    test_dict[comp3] = "value3"

    # comp1 and comp2 are equal, so they should map to the same key
    assert len(test_dict) == 2
    assert test_dict[comp1] == "value2"


def test_http_path_component_deepcopy() -> None:
    """Test deep copying of HttpPathComponent objects."""
    original = HttpPathComponent("test", False)
    copied = copy.deepcopy(original)

    assert copied == original
    assert copied is not original
    assert copied.value == original.value
    assert copied.encoded == original.encoded


def test_http_path_component_deepcopy_encoded() -> None:
    """Test deep copying of encoded HttpPathComponent objects."""
    original = HttpPathComponent("test%20value", True)
    copied = copy.deepcopy(original)

    assert copied == original
    assert copied is not original
    assert copied.value == original.value
    assert copied.encoded == original.encoded


def test_http_path_component_unicode() -> None:
    """Test HttpPathComponent with Unicode characters."""
    comp = HttpPathComponent("✓", False)
    assert comp.value == "✓"
    assert comp.encoded is False


def test_http_path_component_empty_string() -> None:
    """Test HttpPathComponent with empty string."""
    comp = HttpPathComponent("", False)
    assert comp.value == ""
    assert comp.encoded is False

    comp_encoded = HttpPathComponent("", True)
    assert comp_encoded.value == ""
    assert comp_encoded.encoded is True
