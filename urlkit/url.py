"""URL utility library."""

import abc


class URL(abc.ABC):
    """A base URL representation."""

    __slots__ = ()  # Empty slots to allow subclasses to use __slots__
