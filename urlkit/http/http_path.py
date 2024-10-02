"""HTTP Path utilities."""

from typing import Any


class HttpPath:
    """A class representing a path on a HTTP(S) URL."""

    components: list[str]

    def __init__(
        self,
        components: list[str] | None = None,
    ) -> None:
        if components is None:
            self.components = []
        else:
            self.components = components[:]

    def __deepcopy__(self, memo: dict) -> "HttpPath":
        """Copy the HttpPath object."""

        return HttpPath(self.components[:])

    def __eq__(self, other: Any) -> bool:
        """Check if two HttpPath objects are equal."""

        if not isinstance(other, HttpPath):
            return False

        return self.components == other.components

    def __hash__(self) -> int:
        """Get the hash of the HttpPath object."""

        if len(self.components) > 0:
            return hash(tuple(self.components))

        return 0

    def __str__(self) -> str:
        """Get the string representation of the path."""

        path = "/".join(self.components)

        return f"/{path}"

    def append(self, subpath: str | list[str]) -> None:
        """Append a component to the path."""

        if isinstance(subpath, list):
            for component in subpath:
                self.append(component)
        elif "/" in subpath:
            self.components += subpath.split("/")
        else:
            self.components.append(subpath)

    def pop_last(self) -> str:
        """Pop the last component from the path."""

        return self.components.pop()
