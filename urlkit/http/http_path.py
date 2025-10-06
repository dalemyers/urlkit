"""HTTP Path utilities."""

import copy
from dataclasses import dataclass
from typing import Any, Union
import urllib.parse


@dataclass(slots=True)
class HttpPathComponent:
    """A class representing a single component of a HTTP(S) URL path.

    :param value: The value of the path component.
    :param encoded: Whether the value is already percent-encoded.
    """

    value: str
    encoded: bool

    def __eq__(self, other: object) -> bool:
        """Check if two HttpPathComponent objects are equal.

        :param other: The object to compare to.

        :return: True if the objects are equal, False otherwise.
        """

        if not isinstance(other, HttpPathComponent):
            return False

        self_encoded = urllib.parse.quote(self.value) if not self.encoded else self.value
        other_encoded = urllib.parse.quote(other.value) if not other.encoded else other.value

        return self_encoded == other_encoded

    def __hash__(self) -> int:
        """Get the hash of the HttpPathComponent object.

        :return: The hash of the HttpPathComponent object.
        """

        return hash(urllib.parse.quote(self.value) if not self.encoded else self.value)


class HttpPath:
    """A class representing a path on a HTTP(S) URL."""

    __slots__ = ("_components", "trailing_slash")

    _components: list[HttpPathComponent]
    trailing_slash: bool

    def __init__(
        self,
        path: str,
    ) -> None:
        """Initialise the HttpPath object.

        :param components: The components of the path, defaults to None. These
                           would normally be the path split by the '/'
                           character.
        """
        if path is None:
            self._components = []
            self.trailing_slash = False
        else:
            self._normalize_with_path(path)

    def _normalize_with_path(self, path: str) -> None:
        """Normalize a path.

        This is a convenience method that calls the static method
        `remove_dot_segments`.

        :param path: The path to normalize.

        :return: The normalized path.
        """

        path = HttpPath.remove_dot_segments(path)
        if path == "/":
            self._components = []
            self.trailing_slash = True
        else:
            self.trailing_slash = path.endswith("/") and len(path) > 1
            path = path[1:] if path.startswith("/") else path
            path = path[:-1] if self.trailing_slash else path
            components = path.split("/")
            self._components = []
            for c in components:
                # Check if this component appears to be already percent-encoded
                # by checking if it contains valid percent-encoded sequences
                encoded = self._is_percent_encoded(c)
                self._components.append(HttpPathComponent(c, encoded))
            if self._components == [HttpPathComponent("", False)]:
                self._components = []

    @staticmethod
    def _is_percent_encoded(s: str) -> bool:
        """Check if a string appears to be already percent-encoded.

        :param s: The string to check.

        :return: True if the string contains percent-encoded sequences.
        """
        if "%" not in s:
            return False

        # Check if all % signs are followed by valid hex digits
        i = 0
        while i < len(s):
            if s[i] == "%":
                if i + 2 >= len(s):
                    return False
                try:
                    int(s[i + 1 : i + 3], 16)
                    i += 3
                except ValueError:
                    return False
            else:
                i += 1

        return True

    @staticmethod
    def remove_dot_segments(path: str) -> str:
        """Normalize the path components by removing dot-segments.

        This implements the "remove_dot_segments" algorithm from RFC 3986,
        section 5.2.4.

        :param path: The path to normalize.

        :return: The normalized path.
        """

        # Early exit for empty paths
        if not path:
            return ""

        # Special case where there are no segments
        if "/" not in path and path not in (".", ".."):
            return path

        initial_slash = path.startswith("/")
        segments: list[str] = []

        # Since we always assume a path has a prefix slash if not empty, we add
        # it here to make parsing easier.
        if not path.startswith("/"):
            # This avoids case 2A and 2D since we always have a leading slash
            path = "/" + path

        while path:
            if path.startswith("/./"):  # 2B
                path = path[2:]
                continue
            if path == "/.":  # 2B
                path = "/"
                continue
            if path.startswith("/../"):  # 2C
                path = path[3:]
                if segments:
                    segments.pop()
                continue
            if path == "/..":  # 2C
                path = ""
                if segments:
                    segments.pop()
                continue

            # 2E
            slash_index = path.find("/", 1)
            if slash_index == -1:
                segment = path[1:]
                path = ""
            else:
                segment = path[1:slash_index]
                path = path[slash_index:]
            segments.append(segment)
            continue

        output = "/".join(segments)

        if initial_slash:
            output = "/" + output

        return output

    def __deepcopy__(self, memo: dict[int, Any]) -> "HttpPath":
        """Copy the HttpPath object.

        :param memo: The memo dictionary.

        :return: A copy of the HttpPath object.
        """

        c = HttpPath("")
        c._components = self._components[:]
        c.trailing_slash = self.trailing_slash

        return c

    def __eq__(self, other: object) -> bool:
        """Check if two HttpPath objects are equal.

        :param other: The object to compare to.

        :return: True if the objects are equal, False otherwise.
        """

        if not isinstance(other, HttpPath):
            return False

        return self._components == other._components and self.trailing_slash == other.trailing_slash

    def __hash__(self) -> int:
        """Get the hash of the HttpPath object.

        :return: The hash of the HttpPath object.
        """

        if len(self._components) > 0:
            return hash(tuple(self._components))

        return 0

    def __bool__(self) -> bool:
        """Check if the path is non-empty.

        A path is considered truthy if it has components or a trailing slash.
        An empty path (no components and no trailing slash) is falsy.

        :return: True if the path has content, False otherwise.
        """
        return bool(self._components) or self.trailing_slash

    def __str__(self) -> str:
        """Get the string representation of the path.

        :return: The string representation of the path.
        """

        if len(self._components) == 0:
            return "/" if self.trailing_slash else ""

        path = "/" + "/".join(
            component.value if component.encoded else urllib.parse.quote(component.value, safe=";")
            for component in self._components
        )

        if self.trailing_slash:
            path += "/"

        return path

    def __truediv__(self, other: Union[str, "HttpPath"]) -> "HttpPath":
        """Support path / 'segment' syntax like pathlib.Path.

        This creates a new HttpPath with the additional segment(s) appended.
        The original path is not modified.

        :param other: The path segment(s) to append. Can be a string or another HttpPath.

        :return: A new HttpPath with the segment(s) appended.

        Example:
            >>> path = HttpPath("/api")
            >>> new_path = path / "v1" / "users"
            >>> str(new_path)
            '/api/v1/users'
        """
        new_path = copy.deepcopy(self)

        if isinstance(other, str):
            new_path.append(other)
        elif isinstance(other, HttpPath):
            # Append all components from the other path
            for component in other._components:
                new_path._components.append(copy.deepcopy(component))
            # Preserve trailing slash from the other path
            new_path.trailing_slash = other.trailing_slash
            new_path._normalize_with_path(str(new_path))
        else:
            raise TypeError(
                f"unsupported operand type(s) for /: 'HttpPath' and '{type(other).__name__}'"
            )

        return new_path

    def append(self, subpath: str | list[str]) -> None:
        """Append a component to the path.

        :param subpath: The component to append to the path. This can be a
                        string or a list of strings. Any '/' characters in the
                        string will be split into separate components.
        """

        if len(self._components) == 1 and self._components[0].value == "":
            self._components = []

        if isinstance(subpath, list):
            for component in subpath:
                self.append(component)
        elif "/" in subpath:
            self._components += [HttpPathComponent(c, False) for c in subpath.split("/")]
        else:
            self._components.append(HttpPathComponent(subpath, False))

        self._normalize_with_path(str(self))

    def pop_last(self) -> str:
        """Pop the last component from the path.

        :return: The last component of the path.
        """

        value = self._components.pop().value

        if len(self._components) == 1 and self._components[0].value == "":
            self._components = []

        self._normalize_with_path(str(self))

        return value
