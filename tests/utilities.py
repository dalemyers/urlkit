"""Utilities for testing URL construction."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from urlkit import HttpUrl


def assert_http_expected_vs_components(expected: str, url_components: dict) -> None:
    """Test that we can construct URLs correctly."""

    print(expected, url_components)
    url = HttpUrl(**url_components)
    constructed = str(url)
    assert constructed == expected, f"Expected {expected}, got {constructed}"
