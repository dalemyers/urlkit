"""URL utility library."""

from typing import Any


class HttpPath:
    """A class representing a path on a HTTP(S) URL."""

    components: list[str]

    def __init__(
        self,
        components: list[str] | None = None,
    ) -> None:
        self.components = components or []

    def __eq__(self, other: Any) -> bool:
        """Check if two HttpPath objects are equal."""

        if not isinstance(other, HttpPath):
            return False

        return self.components == other.components

    def __hash__(self) -> int:
        """Get the hash of the HttpPath object."""

        return hash(tuple(self.components))

    def __str__(self) -> str:
        """Get the string representation of the path."""

        return "/".join(self.components)

    def append_component(self, component: str) -> None:
        """Append a component to the path."""

        if "/" in component:
            self.extend(component.split("/"))
        else:
            self.components.append(component)

    def extend(self, components: list[str]) -> None:
        """Extend the path with multiple components."""

        for component in components:
            self.append_component(component)

    def pop_last(self) -> str:
        """Pop the last component from the path."""

        return self.components.pop()
