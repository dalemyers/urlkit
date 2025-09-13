"""Test the logic of QuerySet."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from urlkit.http import QuerySet, QueryOptions

# pylint: enable=wrong-import-position

def test_queryset_equality_order_independent():
    """Test that QuerySet equality is order-independent."""
    q1 = QuerySet(QueryOptions(), {"a": "1", "b": "2"})
    q2 = QuerySet(QueryOptions(), {"b": "2", "a": "1"})
    assert q1 == q2, "QuerySet equality should be order-independent"
