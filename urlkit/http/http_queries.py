"""URL utility library."""

import copy
from dataclasses import dataclass
import enum
from typing import Any
import urllib.parse


class SpaceEncoding(enum.Enum):
    """An enumeration representing the various space encoding options."""

    PLUS = "+"
    PERCENT = "%20"


@dataclass(slots=True)
class QueryOptions:
    """A class representing the various query parameter options.

    :param query_joiner: The character used to join query parameters, defaults to "&".
    :param safe_characters: The characters that do not need to be encoded, defaults to "".
    :param space_encoding: The method used to encode spaces, defaults to SpaceEncoding.PERCENT.
    """

    query_joiner: str = "&"
    safe_characters: str = ""
    space_encoding: SpaceEncoding = SpaceEncoding.PERCENT

    def __eq__(self, other: object) -> bool:
        """Check if two QueryOptions objects are equal.

        :param other: The object to compare to.

        :return: True if the objects are equal, False otherwise.
        """

        if not isinstance(other, QueryOptions):
            return False

        return (
            self.query_joiner == other.query_joiner
            and frozenset(self.safe_characters)
            == frozenset(other.safe_characters)  # Order does not matter
            and self.space_encoding == other.space_encoding
        )

    def __hash__(self) -> int:
        """Get the hash of the QueryOptions object.

        :return: The hash of the QueryOptions object.
        """

        return hash(
            (
                self.query_joiner,
                frozenset(self.safe_characters),  # Order does not matter
                self.space_encoding,
            )
        )


@dataclass(slots=True)
class QueryValue:
    """Represents a query value.

    :param value: The value of the query parameter.
    :param encoded: A flag stating whether or not the query parameter is already encoded.
    """

    value: str | bool | int | float
    encoded: bool = False

    def __post_init__(self) -> None:
        """Validate the QueryValue after initialization."""
        if not isinstance(self.value, (str, bool, int, float)):
            raise ValueError(f"Query: Expected str, bool, int, or float, got {type(self.value)}")

    def __eq__(self, other: object) -> bool:
        """Check if two QueryValue objects are equal.

        :param other: The object to compare to.

        :return: True if the objects are equal, False otherwise.
        """

        if not isinstance(other, QueryValue):
            return False

        return self.value == other.value and self.encoded == other.encoded

    def __hash__(self) -> int:
        """Get the hash of the QueryValue object.

        :return: The hash of the QueryValue object.
        """

        return hash((self.value, self.encoded))

    def __str__(self) -> str:
        """Get the string representation of the query value.

        :return: The string representation of the query value.
        """

        return f"<QueryValue value={self.value} encoded={self.encoded}>"

    def __repr__(self) -> str:
        """Get the string representation of the query value.

        :return: The string representation of the query value.
        """

        return self.__str__()


class _QueryValueNone(QueryValue):
    """A class representing a None query value."""

    def __init__(self) -> None:
        """Initialise the _QueryValueNone object."""

        super().__init__(value="", encoded=True)


class QuerySet(dict[str, QueryValue | None]):
    """A class representing a set of query parameters."""

    options: QueryOptions

    def __init__(
        self,
        options: QueryOptions,
        values: dict[str, Any] | None = None,
        assume_unencoded: bool = True,
    ) -> None:
        """Initialise the QuerySet object.

        :param options: The query parameter options.
        :param values: The query parameters, defaults to None.
        :param assume_unencoded: A flag stating whether or not the query parameters are already encoded.
        """

        self.options = options
        super().__init__()

        if values:
            for k, v in values.items():
                self.__setitem_encoded(k, v, not assume_unencoded)

    def __deepcopy__(self, memo: dict[int, Any]) -> "QuerySet":
        """Copy the QuerySet object.

        :param memo: The memo dictionary.

        :return: A copy of the QuerySet object.
        """

        new_values = {}

        for key in self.keys():
            value = super().__getitem__(key)
            new_values[key] = copy.deepcopy(value, memo)

        return QuerySet(self.options, values=new_values, assume_unencoded=False)

    def __setitem_encoded(self, key: str, value: Any, encoded: bool) -> None:
        """Set the query parameter and the flag stating whether or not it is encoded.

        :param key: The key of the query parameter.
        :param value: The value of the query parameter.
        :param encoded: A flag stating whether or not the query parameter is already encoded.
        """

        if value is None:
            super().__setitem__(key, _QueryValueNone())
        elif isinstance(value, QueryValue):
            super().__setitem__(key, value)
        else:
            super().__setitem__(key, QueryValue(value, encoded=encoded))

    def __setitem__(self, key: str, value: Any | None) -> None:
        """Set a query parameter.

        :param key: The key of the query parameter.
        :param value: The value of the query parameter.
        """

        self.__setitem_encoded(key, value, encoded=False)

    def __getitem__(self, key: str) -> QueryValue | None:
        """Get a query parameter.

        :param key: The key of the query parameter.

        :return: The value of the query parameter.
        """

        value = super().__getitem__(key)

        # We have this as a special case so that we can have a named parameter
        # added, without it having a value.
        if isinstance(value, _QueryValueNone):
            return None

        return value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a query parameter with a default value.

        :param key: The key of the query parameter.
        :param default: The default value to return if the query parameter does
                        not exist.

        :return: The value of the query parameter or the default value.
        """

        try:
            return self[key]
        except KeyError:
            return default

    def set_encoded(self, key: str, value: str) -> None:
        """Set a query parameter as encoded.

        :param key: The key of the query parameter.
        :param value: The value of the query parameter.
        """

        super().__setitem__(key, QueryValue(value, encoded=True))

    def set_none_value(self, key: str) -> None:
        """Set a query parameter as None.

        :param key: The key of the query parameter.
        """

        super().__setitem__(key, _QueryValueNone())  # type: ignore

    def __str__(self) -> str:
        """Get the string representation of the query set.

        :return: The string representation of the query set.
        """

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

            if value is None or isinstance(value, _QueryValueNone):
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

    def __eq__(self, other: object) -> bool:
        """Check if two QuerySet objects are equal.

        :param other: The object to compare to.

        :return: True if the objects are equal, False otherwise.
        """

        if not isinstance(other, QuerySet):
            return False

        if self.options != other.options:
            return False

        if len(self.items()) != len(other.items()):
            return False

        for k1 in self.keys():
            if k1 not in other:
                return False
            self_value = self[k1]
            other_value = other[k1]
            if self_value != other_value:
                return False

        return True

    def __ne__(self, other: object) -> bool:
        """Check if two QuerySet objects are not equal."""

        return not self.__eq__(other)


def decode_query_value(value: str, options: QueryOptions) -> str:
    """Decode a query value.

    :param value: The value to decode.
    :param options: The query parameter options.

    :return: The decoded value.
    """

    if options.space_encoding == SpaceEncoding.PERCENT:
        return urllib.parse.unquote(value)

    if options.space_encoding == SpaceEncoding.PLUS:
        return urllib.parse.unquote_plus(value)

    raise ValueError(f"Space Encoding: Expected valid SpaceEncoding, got {options.space_encoding}")
