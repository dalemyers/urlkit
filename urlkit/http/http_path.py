"""HTTP Path utilities."""

from typing import Any


class HttpPath:
    """A class representing a path on a HTTP(S) URL."""

    components: list[str]

    def __init__(
        self,
        components: list[str] | None = None,
    ) -> None:
        """Initialise the HttpPath object.

        :param components: The components of the path, defaults to None. These
                           would normally be the path split by the '/'
                           character.
        """
        if components is None:
            self.components = []
        else:
            self.components = components[:]

    def __deepcopy__(self, memo: dict[int, Any]) -> "HttpPath":
        """Copy the HttpPath object.

        :param memo: The memo dictionary.

        :return: A copy of the HttpPath object.
        """

        return HttpPath(self.components[:])

    def __eq__(self, other: object) -> bool:
        """Check if two HttpPath objects are equal.

        :param other: The object to compare to.

        :return: True if the objects are equal, False otherwise.
        """

        if not isinstance(other, HttpPath):
            return False

        return self.components == other.components

    def __hash__(self) -> int:
        """Get the hash of the HttpPath object.

        :return: The hash of the HttpPath object.
        """

        if len(self.components) > 0:
            return hash(tuple(self.components))

        return 0

    def __str__(self) -> str:
        """Get the string representation of the path.

        :return: The string representation of the path.
        """

        path = "/".join(self.components)

        return f"/{path}"

    def append(self, subpath: str | list[str]) -> None:
        """Append a component to the path.

        :param subpath: The component to append to the path. This can be a
                        string or a list of strings. Any '/' characters in the
                        string will be split into separate components.
        """

        if isinstance(subpath, list):
            for component in subpath:
                self.append(component)
        elif "/" in subpath:
            self.components += subpath.split("/")
        else:
            self.components.append(subpath)

    def pop_last(self) -> str:
        """Pop the last component from the path.

        :return: The last component of the path.
        """

        return self.components.pop()
