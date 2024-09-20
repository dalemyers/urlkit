"""URL utility library."""

from typing import Any

from .url import URL
from .http_queries import encode_query, QueryOptions


class BaseHttpOrHttpsUrl(URL):
    """A HTTP URL representation."""

    scheme: str
    host: str
    port: int | None
    path: str | None
    query: dict[str, Any] | str | None
    fragment: str | None
    query_options: QueryOptions

    def __init__(
        self,
        *,
        scheme: str,
        host: str,
        port: int | str | None = None,
        path: str | None = None,
        query: dict[str, Any] | str | None = None,
        fragment: str | None = None,
        query_options: QueryOptions = QueryOptions(),
    ) -> None:
        super().__init__()

        self.scheme = scheme
        self.host = host
        self.path = path
        self.query = query
        self.fragment = fragment
        self.query_options = query_options

        if scheme not in ("http", "https"):
            raise ValueError(f"Scheme: Expected 'http' or 'https', got {scheme}")

        if not isinstance(self.host, str):
            raise TypeError(f"Host: Expected str, got {type(self.host)}")

        if port is not None:
            try:
                self.port = int(port)
            except ValueError as ex:
                raise ValueError(f"Port: Expected valid integer value, got {port}") from ex
        else:
            self.port = None

        if self.path is not None and not isinstance(self.path, str):
            raise TypeError(f"Path: Expected str or None, got {type(self.path)}")

        if (
            self.query is not None
            and not isinstance(self.query, dict)
            and not isinstance(self.query, str)
        ):
            raise TypeError(f"Query: Expected dict, str, or None, got {type(self.query)}")

        if self.fragment is not None and not isinstance(self.fragment, str):
            raise TypeError(f"Fragment: Expected str or None, got {type(self.fragment)}")

    def __str__(self) -> str:
        """Construct the URL string representation."""

        output = f"{self.scheme}://{self.host}"

        if self.port:
            output += f":{self.port}"

        if self.path:
            output += self.path

        # We usually see the root path if a query is there.
        if not self.path and self.query:
            output += "/"

        if self.query:
            output += self.query_options.query_separator + encode_query(
                self.query, self.query_options
            )

        if self.fragment:
            output += "#" + self.fragment

        return output

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self})"


class HttpUrl(BaseHttpOrHttpsUrl):
    """A HTTP URL representation."""

    def __init__(
        self,
        *,
        host: str,
        port: int | str | None = None,
        path: str | None = None,
        query: dict[str, Any] | str | None = None,
        fragment: str | None = None,
        query_options: QueryOptions = QueryOptions(),
    ) -> None:
        super().__init__(
            scheme="http",
            host=host,
            port=port,
            path=path,
            query=query,
            fragment=fragment,
            query_options=query_options,
        )


class HttpsUrl(BaseHttpOrHttpsUrl):
    """A HTTPS URL representation."""

    def __init__(
        self,
        *,
        host: str,
        port: int | str | None = None,
        path: str | None = None,
        query: dict[str, Any] | str | None = None,
        fragment: str | None = None,
        query_options: QueryOptions = QueryOptions(),
    ) -> None:
        super().__init__(
            scheme="https",
            host=host,
            port=port,
            path=path,
            query=query,
            fragment=fragment,
            query_options=query_options,
        )
