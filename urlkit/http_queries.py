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


def encode_query(query: dict[str, Any], options: QueryOptions) -> str:
    """Encode a query dictionary into a query string."""

    encoded_values = []

    if options.space_encoding == SpaceEncoding.PERCENT:
        encoding_function = urllib.parse.quote
    elif options.space_encoding == SpaceEncoding.PLUS:
        encoding_function = urllib.parse.quote_plus
    else:
        raise ValueError(
            f"Space Encoding: Expected valid SpaceEncoding, got {options.space_encoding}"
        )

    for key, value in query.items():
        encoded_key = encoding_function(key, safe=options.safe_characters)

        if value is None:
            encoded_values.append(encoded_key)
            continue

        if isinstance(value, str):
            encoded_value = encoding_function(value, safe=options.safe_characters)
        elif isinstance(value, bool):  # Must be above int
            encoded_value = "true" if value else "false"
        elif isinstance(value, int):
            encoded_value = str(value)
        elif isinstance(value, float):
            encoded_value = str(value)
        else:
            raise ValueError(f"Query: Expected str or int, got {type(value)}")

        encoded_values.append(f"{encoded_key}={encoded_value}")

    return options.query_joiner.join(encoded_values)


def decode_query_value(value: str, options: QueryOptions) -> str:
    """Decode a query value."""

    if options.space_encoding == SpaceEncoding.PERCENT:
        return urllib.parse.unquote(value)

    if options.space_encoding == SpaceEncoding.PLUS:
        return urllib.parse.unquote_plus(value)

    raise ValueError(f"Space Encoding: Expected valid SpaceEncoding, got {options.space_encoding}")
