"""HTTP Path utilities."""

from typing import Any


class HttpPath:
    """A class representing a path on a HTTP(S) URL."""

    components: list[str]
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
            self.components = []
            self.trailing_slash = False
        else:
            path = HttpPath.remove_dot_segments(path)
            self.trailing_slash = path.endswith("/") and len(path) > 1
            path = path[1:] if path.startswith("/") else path
            path = path[:-1] if self.trailing_slash else path
            self.components = path.split("/")
            if self.components == [""]:
                self.components = []

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
        segments = []

        # Since we always assume a path has a prefix slash if not empty, we add
        # it here to make parsing easier.
        if not path.startswith("/"):
            path = "/" + path

        while path:
            if path.startswith("../"):  # 2A
                path = path[3:]
                continue
            if path.startswith("./"):  # 2A
                path = path[2:]
                continue
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
                path = "/"
                if segments:
                    segments.pop()
                continue
            if path == "." or path == "..":  # 2D
                path = ""
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
        c.components = self.components[:]
        c.trailing_slash = self.trailing_slash

        return c

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

        path = "/" + "/".join(self.components)

        if self.trailing_slash:
            path += "/"

        return path

    def append(self, subpath: str | list[str]) -> None:
        """Append a component to the path.

        :param subpath: The component to append to the path. This can be a
                        string or a list of strings. Any '/' characters in the
                        string will be split into separate components.
        """

        if len(self.components) == 1 and self.components[0] == "":
            self.components = []

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

        value = self.components.pop()

        if len(self.components) == 1 and self.components[0] == "":
            self.components = []

        return value
