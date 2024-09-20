"""URL utility library."""

from typing import Any

from .url import URL
from .http_queries import encode_query, QueryOptions


class BaseHttpOrHttpsUrl(URL):
    """A HTTP URL representation."""

    _scheme: str
    _host: str
    _port: int | None
    _path: str | None
    _query: dict[str, Any] | str | None
    _fragment: str | None
    _query_options: QueryOptions

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
        self.port = port
        self.path = path
        self.query = query
        self.fragment = fragment
        self.query_options = query_options

    def __str__(self) -> str:
        """Construct the URL string representation."""

        output = f"{self._scheme}://{self._host}"

        if self._port:
            output += f":{self._port}"

        if self._path:
            output += self._path

        # We usually see the root path if a query is there.
        if not self._path and self._query:
            output += "/"

        if self._query:
            output += self._query_options.query_separator + encode_query(
                self._query, self._query_options
            )

        if self._fragment:
            output += "#" + self._fragment

        return output

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self})"

    @property
    def scheme(self) -> str:
        """Get the URL scheme."""
        return self._scheme

    @scheme.setter
    def scheme(self, value: str) -> None:
        """Set the URL scheme."""
        if value not in ("http", "https"):
            raise ValueError(f"Scheme: Expected 'http' or 'https', got {value}")

        self._scheme = value

    @property
    def host(self) -> str:
        """Get the URL host."""
        return self._host

    @host.setter
    def host(self, value: str) -> None:
        """Set the URL host."""
        if not isinstance(value, str):
            raise TypeError(f"Host: Expected str, got {type(value)}")

        self._host = value

    @property
    def port(self) -> int | str | None:
        """Get the URL port."""
        return self._port

    @port.setter
    def port(self, value: int | str | None) -> None:
        """Set the URL port."""
        if value is None:
            self._port = None
            return

        try:
            port_value = int(value)

            if port_value < 0 or port_value > 65535:
                raise ValueError(f"Port: Expected value between 0 and 65535, got {port_value}")

            self._port = port_value
        except ValueError as ex:
            raise ValueError(f"Port: Expected valid integer value, got {value}") from ex

    @property
    def path(self) -> str | None:
        """Get the URL path."""
        return self._path

    @path.setter
    def path(self, value: str | None) -> None:
        """Set the URL path."""
        if value is not None and not isinstance(value, str):
            raise TypeError(f"Path: Expected str or None, got {type(value)}")

        self._path = value

    @property
    def query(self) -> dict[str, Any] | str | None:
        """Get the URL query."""
        return self._query

    @query.setter
    def query(self, value: dict[str, Any] | str | None) -> None:
        """Set the URL query."""
        if value is not None and not isinstance(value, dict) and not isinstance(value, str):
            raise TypeError(f"Query: Expected dict, str, or None, got {type(value)}")

        self._query = value

    @property
    def fragment(self) -> str | None:
        """Get the URL fragment."""
        return self._fragment

    @fragment.setter
    def fragment(self, value: str | None) -> None:
        """Set the URL fragment."""
        if value is not None and not isinstance(value, str):
            raise TypeError(f"Fragment: Expected str or None, got {type(value)}")

        self._fragment = value

    @property
    def query_options(self) -> QueryOptions | None:
        """Get the URL query options."""
        return self._query_options

    @query_options.setter
    def query_options(self, value: QueryOptions) -> None:
        """Set the URL query options."""
        if not isinstance(value, QueryOptions):
            raise TypeError(f"Query options: Expected QueryOptions got {type(value)}")

        self._query_options = value


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
