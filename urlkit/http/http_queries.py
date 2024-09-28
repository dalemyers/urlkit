"""URL utility library."""

import enum
from typing import Any
import urllib.parse


class SpaceEncoding(enum.Enum):
    """An enumeration representing the various space encoding options."""

    PLUS = "+"
    PERCENT = "%20"


class QueryOptions:
    """A class representing the various query parameter options."""

    query_joiner: str
    safe_characters: str
    space_encoding: SpaceEncoding

    def __init__(
        self,
        query_joiner: str = "&",
        safe_characters: str = "",
        space_encoding: SpaceEncoding = SpaceEncoding.PERCENT,
    ) -> None:
        self.query_joiner = query_joiner
        self.safe_characters = safe_characters
        self.space_encoding = space_encoding

    def __eq__(self, other: Any) -> bool:
        """Check if two QueryOptions objects are equal."""

        if not isinstance(other, QueryOptions):
            return False

        return (
            self.query_joiner == other.query_joiner
            and self.safe_characters == other.safe_characters
            and self.space_encoding == other.space_encoding
        )

    def __hash__(self) -> int:
        """Get the hash of the QueryOptions object."""

        return hash(
            (
                self.query_joiner,
                self.safe_characters,
                self.space_encoding,
            )
        )


class QueryValue:
    """Represents a query value."""

    value: str | bool | int | float
    encoded: bool

    def __init__(self, value: str | bool | int | float, encoded: bool = False) -> None:

        if not isinstance(value, (str, bool, int, float)):
            raise ValueError(f"Query: Expected str, bool, int, or float, got {type(value)}")

        self.value = value
        self.encoded = encoded

    def __eq__(self, other: Any) -> bool:
        """Check if two QueryValue objects are equal."""

        if not isinstance(other, QueryValue):
            return False

        return self.value == other.value and self.encoded == other.encoded

    def __hash__(self) -> int:
        """Get the hash of the QueryValue object."""

        return hash((self.value, self.encoded))

    def __str__(self) -> str:
        """Get the string representation of the query value."""

        return f"<QueryValue value={self.value} encoded={self.encoded}>"

    def __repr__(self) -> str:
        """Get the string representation of the query value."""

        return self.__str__()


class QuerySet(dict[str, QueryValue]):
    """A class representing a set of query parameters."""

    _NONE_SENTINEL = object()

    options: QueryOptions

    def __init__(
        self,
        options: QueryOptions,
        values: dict[str, Any] | None = None,
        assume_unencoded: bool = True,
    ) -> None:
        self.options = options
        super().__init__()

        if values:
            for k, v in values.items():
                self.__setitem_encoded(k, v, not assume_unencoded)

    def __setitem_encoded(self, key: str, value: Any, encoded: bool) -> None:
        """Set the query parameter and the flag stating whether or not it is encoded.

        :param key: The key of the query parameter.
        :param value: The value of the query parameter.
        :param encoded: A flag stating whether or not the query parameter is already encoded.
        """

        if value is None:
            super().__setitem__(key, QuerySet._NONE_SENTINEL)  # type: ignore
        elif isinstance(value, QueryValue):
            super().__setitem__(key, value)
        else:
            super().__setitem__(key, QueryValue(value, encoded=encoded))

    def __setitem__(self, key: str, value: Any | None) -> None:
        """Set a query parameter."""

        self.__setitem_encoded(key, value, encoded=False)

    def __getitem__(self, key: str) -> Any:
        """Get a query parameter."""

        value = super().__getitem__(key)

        if value is QuerySet._NONE_SENTINEL:
            return None

        return value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a query parameter with a default value."""

        try:
            return self[key]
        except KeyError:
            return default

    def set_encoded(self, key: str, value: str) -> None:
        """Set a query parameter as encoded."""

        super().__setitem__(key, QueryValue(value, encoded=True))

    def set_none_value(self, key: str) -> None:
        """Set a query parameter as None."""

        super().__setitem__(key, QuerySet._NONE_SENTINEL)  # type: ignore

    def __str__(self) -> str:
        """Get the string representation of the query set."""

        encoded_values = []

        if self.options.space_encoding == SpaceEncoding.PERCENT:
            encoding_function = urllib.parse.quote
        elif self.options.space_encoding == SpaceEncoding.PLUS:
            encoding_function = urllib.parse.quote_plus
        else:
            raise ValueError(
                f"Space Encoding: Expected valid SpaceEncoding, got {self.options.space_encoding}"
            )

        for key, value in self.items():
            encoded_key = encoding_function(key, safe=self.options.safe_characters)

            if value is None or value is QuerySet._NONE_SENTINEL:
                encoded_values.append(encoded_key)
                continue

            assert isinstance(value, QueryValue), f"Query: Expected QueryValue, got {type(value)}"

            if value.encoded:
                encoded_values.append(f"{encoded_key}={value.value}")
                continue

            if isinstance(value.value, str):
                encoded_value = encoding_function(value.value, safe=self.options.safe_characters)
            elif isinstance(value.value, bool):  # Must be above int
                encoded_value = "true" if value.value else "false"
            elif isinstance(value.value, int):
                encoded_value = str(value.value)
            elif isinstance(value.value, float):
                encoded_value = str(value.value)
            else:
                raise ValueError(f"Query: Expected str, bool, or int, got {type(value.value)}")

            encoded_values.append(f"{encoded_key}={encoded_value}")

        return self.options.query_joiner.join(encoded_values)

    def __eq__(self, other: Any) -> bool:
        """Check if two QuerySet objects are equal."""

        if not isinstance(other, QuerySet):
            return False

        if self.options != other.options:
            return False

        for (k1, v1), (k2, v2) in zip(self.items(), other.items()):
            if k1 != k2 or v1 != v2:
                return False

        return len(self.items()) == len(other.items())

    def __ne__(self, other: Any) -> bool:
        """Check if two QuerySet objects are not equal."""

        return not self.__eq__(other)


def decode_query_value(value: str, options: QueryOptions) -> str:
    """Decode a query value."""

    if options.space_encoding == SpaceEncoding.PERCENT:
        return urllib.parse.unquote(value)

    if options.space_encoding == SpaceEncoding.PLUS:
        return urllib.parse.unquote_plus(value)

    raise ValueError(f"Space Encoding: Expected valid SpaceEncoding, got {options.space_encoding}")
