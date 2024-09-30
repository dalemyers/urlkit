"""HTTP Path utilities."""

from typing import Any


class HttpPath:
    """A class representing a path on a HTTP(S) URL."""

    components: list[str]
    _from_root: bool
    _is_empty: bool = False

    def __init__(
        self,
        components: list[str],
        from_root: bool = False,
        is_empty: bool = False,
    ) -> None:
        if is_empty:
            self.components = []
            self.from_root = False
            self._is_empty = True
        else:
            self.components = components[:]
            self.from_root = from_root
            self._is_empty = False

    def __deepcopy__(self, memo: dict) -> "HttpPath":
        """Copy the HttpPath object."""

        return HttpPath(self.components[:], self.from_root, self.is_empty)

    def __eq__(self, other: Any) -> bool:
        """Check if two HttpPath objects are equal."""

        if not isinstance(other, HttpPath):
            return False

        if other.is_empty and self.is_empty:
            return True

        return self.components == other.components and self.from_root == other.from_root

    def __hash__(self) -> int:
        """Get the hash of the HttpPath object."""

        return hash((*self.components, self.from_root, self.is_empty))

    def __str__(self) -> str:
        """Get the string representation of the path."""

        if self.is_empty:
            return ""

        path = "/".join(self.components)

        if self.from_root:
            return f"/{path}"

        return path

    @property
    def from_root(self) -> bool:
        """Get the from_root property."""

        return self._from_root

    @from_root.setter
    def from_root(self, value: bool) -> None:
        """Set the from_root property."""

        self._from_root = value
        self.is_empty = False

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
