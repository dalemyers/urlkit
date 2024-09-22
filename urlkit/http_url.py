"""URL utility library."""

from typing import Any, cast, Union

from .url import URL
from .http_queries import encode_query, QueryOptions, decode_query_value
from .http_path import HttpPath


class BaseHttpOrHttpsUrl(URL):
    """A HTTP URL representation."""

    _scheme: str
    _username: str | None
    _password: str | None
    _host: str
    _port: int | None
    _path: HttpPath | None
    _query: dict[str, Any] | None
    _fragment: str | None
    _query_options: QueryOptions

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        *,
        scheme: str,
        username: str | None = None,
        password: str | None = None,
        host: str,
        port: int | str | None = None,
        path: str | HttpPath | None = None,
        query: dict[str, Any] | str | None = None,
        fragment: str | None = None,
        query_options: QueryOptions = QueryOptions(),
    ) -> None:
        super().__init__()

        self.scheme = scheme
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.path = path
        # Needs to be set before query as we use it in the query setter
        self.query_options = query_options
        self.query = query  # type: ignore
        self.fragment = fragment

    # pylint: enable=too-many-arguments

    def __str__(self) -> str:
        """Construct the URL string representation."""

        output = f"{self._scheme}://"

        if self.username:
            output += self.username

            if self.password:
                output += f":{self.password}"

            output += "@"

        output += self._host

        if self._port:
            output += f":{self._port}"

        if self._path:
            output += str(self._path)

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

    def __eq__(self, other: object) -> bool:
        """Check if two URL objects are equal."""

        if not isinstance(other, BaseHttpOrHttpsUrl):
            return False

        return (
            self._scheme == other.scheme
            and self._host == other.host
            and self._port == other.port
            and self._path == other.path
            and self._query == other.query
            and self._fragment == other.fragment
            and self._query_options == other.query_options
        )

    def __hash__(self) -> int:
        """Get the hash of the URL object."""

        if isinstance(self._query, dict):
            query_hashable: Any = frozenset(self._query.items())
        else:
            query_hashable = self._query

        return hash(
            (
                self._scheme,
                self._host,
                self._port,
                self._path,
                query_hashable,
                self._fragment,
                self._query_options,
            )
        )

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
    def username(self) -> str | None:
        """Get the URL username."""
        return self._username

    @username.setter
    def username(self, value: str) -> None:
        """Set the URL username."""
        self._username = value

    @property
    def password(self) -> str | None:
        """Get the URL password."""
        return self._password

    @password.setter
    def password(self, value: str) -> None:
        """Set the URL password."""
        self._password = value

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
    def netloc(self) -> str:
        """Get the netloc as defined by RFC1808."""
        output = ""

        if self.username:
            output += self.username

            if self.password:
                output += f":{self.password}"

            output += "@"

        output += self.host

        if self.port:
            output += f":{self.port}"

        return output

    @property
    def path(self) -> HttpPath | str | None:
        """Get the URL path."""
        return self._path

    @path.setter
    def path(self, value: str | HttpPath | None) -> None:
        """Set the URL path."""
        if value is None:
            self._path = None
            return

        if isinstance(value, str):
            self._path = HttpPath(value.split("/"))
            return

        if isinstance(value, HttpPath):
            self._path = value
            return

        raise TypeError(f"Path: Expected str, HttpPath, or None, got {type(value)}")

    @property
    def query(self) -> dict[str, Any] | None:
        """Get the URL query."""
        return self._query

    @query.setter
    def query(self, value: dict[str, Any] | str | None) -> None:
        """Set the URL query."""
        if value is not None and not isinstance(value, dict) and not isinstance(value, str):
            raise TypeError(f"Query: Expected dict, str, or None, got {type(value)}")

        if value is None or isinstance(value, dict):
            self._query = value
            return

        # If it's a string, we need to parse it into a dict.

        components = value.split(self.query_options.query_joiner)

        query_dict: dict[str, Any] = {}

        for component in components:
            key_value = component.split(self.query_options.key_value_separator, maxsplit=1)

            key = decode_query_value(key_value[0], self.query_options)

            if len(key_value) == 1:
                query_dict[key] = None
            else:
                query_dict[key] = decode_query_value(key_value[1], self.query_options)

        self._query = query_dict

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
    def query_options(self) -> QueryOptions:
        """Get the URL query options."""
        return self._query_options

    @query_options.setter
    def query_options(self, value: QueryOptions) -> None:
        """Set the URL query options."""
        if not isinstance(value, QueryOptions):
            raise TypeError(f"Query options: Expected QueryOptions got {type(value)}")

        self._query_options = value

    @classmethod
    def parse(
        cls, string: str, query_options: QueryOptions = QueryOptions()
    ) -> Union["HttpUrl", "HttpsUrl"]:
        """Parse a URL string into a URL object."""

        result = parse_http_or_https_url(string, query_options)

        if result.scheme == "http":
            return cast(HttpUrl, result)

        return cast(HttpsUrl, result)


class HttpUrl(BaseHttpOrHttpsUrl):
    """A HTTP URL representation."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        *,
        username: str | None = None,
        password: str | None = None,
        host: str,
        port: int | str | None = None,
        path: str | None = None,
        query: dict[str, Any] | str | None = None,
        fragment: str | None = None,
        query_options: QueryOptions = QueryOptions(),
    ) -> None:
        super().__init__(
            scheme="http",
            username=username,
            password=password,
            host=host,
            port=port,
            path=path,
            query=query,
            fragment=fragment,
            query_options=query_options,
        )

    # pylint: enable=too-many-arguments

    @classmethod
    def parse(cls, string: str, query_options: QueryOptions = QueryOptions()) -> "HttpUrl":
        """Parse a URL string into a URL object."""

        if not string.startswith("http://"):
            raise ValueError("URL: Expected 'http://' prefix")

        parsed = BaseHttpOrHttpsUrl.parse(string, query_options)

        return HttpUrl(
            username=parsed.username,
            password=parsed.password,
            host=parsed.host,
            port=parsed.port,
            path=parsed.path,  # type: ignore
            query=parsed.query,
            fragment=parsed.fragment,
            query_options=parsed.query_options,
        )


class HttpsUrl(BaseHttpOrHttpsUrl):
    """A HTTPS URL representation."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        *,
        username: str | None = None,
        password: str | None = None,
        host: str,
        port: int | str | None = None,
        path: str | None = None,
        query: dict[str, Any] | str | None = None,
        fragment: str | None = None,
        query_options: QueryOptions = QueryOptions(),
    ) -> None:
        super().__init__(
            scheme="https",
            username=username,
            password=password,
            host=host,
            port=port,
            path=path,
            query=query,
            fragment=fragment,
            query_options=query_options,
        )

    # pylint: disable=too-many-arguments

    @classmethod
    def parse(cls, string: str, query_options: QueryOptions = QueryOptions()) -> "HttpsUrl":
        """Parse a URL string into a URL object."""

        if not string.startswith("https://"):
            raise ValueError("URL: Expected 'https://' prefix")

        parsed = BaseHttpOrHttpsUrl.parse(string, query_options)

        return HttpsUrl(
            username=parsed.username,
            password=parsed.password,
            host=parsed.host,
            port=parsed.port,
            path=parsed.path,  # type: ignore
            query=parsed.query,
            fragment=parsed.fragment,
            query_options=parsed.query_options,
        )


# pylint: disable=too-many-branches
def parse_http_or_https_url(
    value: str, query_options: QueryOptions = QueryOptions()
) -> BaseHttpOrHttpsUrl:
    """Parse a HTTP or HTTPS URL."""

    # This comes from https://datatracker.ietf.org/doc/html/rfc1738
    # There are some liberties taken. For example, according to their BNF
    # grammar, you can't have a username and password for a HTTP(s) url, only
    # for FTP, etc. And HTTPS doesn't event exist in the spec yet.

    # TODO: This can probably be made much more efficient

    # Anything at the start we know is the scheme.
    if value.startswith("http://"):
        scheme = "http"
        value = value[7:]
    elif value.startswith("https://"):
        scheme = "https"
        value = value[8:]
    else:
        raise ValueError("URL: Expected 'http://' or 'https://' prefix")

    # Anything at the end after a # we know is the fragment.
    fragment_index = value.find("#")

    if fragment_index != -1:
        fragment = value[fragment_index + 1 :]
        value = value[:fragment_index]
    else:
        fragment = None

    # We assume there are no characters in the query that also match the query
    # separator (usually ?).

    query_index = value.rfind(query_options.query_separator)

    if query_index != -1:
        query = value[query_index + 1 :]
        value = value[:query_index]
    else:
        query = None

    # Now we assume there are no `@` characters in the host, port or login
    # details. This isn't necessarily true, but it's a good assumption for now.

    login_index = value.find("@")

    if login_index != -1:
        login = value[:login_index]
        value = value[login_index + 1 :]
    else:
        login = None

    host = value

    # If we have a login, we still need to split into username and password (if
    # there is a password).
    if login:
        password_index = login.find(":")

        if password_index != -1:
            password = login[password_index + 1 :]
            username = login[:password_index]
        else:
            username = login
            password = None
    else:
        username = None
        password = None

    # Now it gets a little trickier. There may be a `:` for the port, but this
    # also often appears in the path. We need to check if it's a port or not.

    # We assume that if it appears before the first `/` then it's a port,
    # otherwise it's part of the path.

    path_index = value.find("/")
    port_index = value.find(":")

    def get_port(port_string: str) -> int | None:
        try:
            return int(port_string)
        except ValueError:
            return None

    if port_index == -1 and path_index == -1:
        port = None
        path = None
        host = value
    elif port_index == -1 and path_index != -1:
        port = None
        path = value[path_index:]
        host = value[:path_index]
    elif port_index != -1 and path_index == -1:
        port_string = value[port_index + 1 :]
        port = get_port(port_string)
        path = None
        host = value[:port_index]
    else:
        if port_index < path_index:
            port_string = value[port_index + 1 : path_index]
            port = get_port(port_string)
            path = value[path_index:]
            host = value[:port_index]
        else:
            port = None
            path = value[path_index:]
            host = value[:path_index]

    if scheme == "http":
        return HttpUrl(
            username=username,
            password=password,
            host=host,
            port=port,
            path=path,
            query=query,
            fragment=fragment,
            query_options=query_options,
        )

    return HttpsUrl(
        username=username,
        password=password,
        host=host,
        port=port,
        path=path,
        query=query,
        fragment=fragment,
        query_options=query_options,
    )


# pylint: enable=too-many-branches
