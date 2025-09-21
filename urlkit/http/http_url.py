"""URL utility library."""

import copy
from typing import Any, cast, Literal

from ..url import URL
from .http_queries import QueryOptions, decode_query_value, QueryValue, QuerySet
from .http_path import HttpPath


class HttpUrl(URL):
    """A HTTP(s) URL representation."""

    _scheme: Literal["http", "https"]
    _username: str | None
    _password: str | None
    _host: str | None
    _port: int | None
    _path: HttpPath
    _query: QuerySet
    _fragment: str | None
    _query_options: QueryOptions

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        *,
        scheme: Literal["http", "https"],
        username: str | None = None,
        password: str | None = None,
        host: str | None,  # This is usually set, so we won't give a default.
        port: int | str | None = None,
        path: str | HttpPath | None = None,
        query: dict[str, str | bool | int | float | QueryValue] | str | QuerySet | None = None,
        fragment: str | None = None,
        query_options: QueryOptions = QueryOptions(),
    ) -> None:
        """Create a new URL object.

        :param scheme: The URL scheme. This should be either 'http' or 'https'.
        :param username: The username for the URL, defaults to None.
        :param password: The password for the URL, defaults to None.
        :param host: The URL host.
        :param port: The URL port, defaults to None.
        :param path: The URL path, defaults to None. This can be a string, or an
                     HttpPath object.
        :param query: The URL query, defaults to None. This can be a dict, a
                      string, or a QuerySet object. If it is a dict, the values
                      can be QueryValue objects, a string, a number or a
                      boolean.
        :param fragment: The URL fragment, defaults to None.
        :param query_options: The query options for the URL, defaults to an
                              empty QueryOptions object (with defaults).
        """

        super().__init__()

        self.scheme = scheme
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.path = path if path else HttpPath()  # type: ignore
        # Needs to be set before query as we use it in the query setter
        self.query_options = query_options
        self.query = query
        self.fragment = fragment

    # pylint: enable=too-many-arguments

    def __deepcopy__(self, memo: dict) -> "HttpUrl":
        """Create a copy of the URL object.

        :param memo: The memo dictionary.

        :return: A copy of the URL object.
        """

        return HttpUrl(
            scheme=self.scheme,
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            path=copy.deepcopy(self.path, memo),
            query=copy.deepcopy(self.query, memo),
            fragment=self.fragment,
            query_options=copy.deepcopy(self.query_options, memo),
        )

    def copy(self) -> "HttpUrl":
        """Create a copy of the URL object.

        :return: A copy of the URL object.
        """
        return copy.deepcopy(self)

    def __str__(self) -> str:
        """Construct the URL string representation.

        :return: The URL string representation.
        """

        output = f"{self._scheme}:"

        if netloc := self.netloc:
            output += "//" + netloc

        if self._path and len(self._path.components) > 0:
            output += str(self._path)
        elif self._query:
            output += "/"

        if self._query:
            output += f"?{self._query}"

        if self._fragment:
            output += "#" + self._fragment

        return output

    def __repr__(self) -> str:
        """Construct the URL representation.

        :return: The URL representation.
        """
        return f"{self.__class__.__name__}({self})"

    def __eq__(self, other: object) -> bool:
        """Check if two URL objects are equal.

        :param other: The object to compare to.

        :return: True if the objects are equal, False otherwise.
        """

        if not isinstance(other, HttpUrl):
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
    def scheme(self) -> Literal["http", "https"]:
        """Get the URL scheme.

        :return: The URL scheme.
        """
        return cast(Literal["http", "https"], self._scheme)

    @scheme.setter
    def scheme(self, value: Literal["http", "https"]) -> None:
        """Set the URL scheme.

        :param value: The URL scheme.

        :raises ValueError: If the scheme is not 'http' or 'https'.
        """
        if value not in ("http", "https"):
            raise ValueError(f"Scheme: Expected 'http' or 'https', got {value}")

        self._scheme = value

    @property
    def username(self) -> str | None:
        """Get the URL username.

        :return: The URL username.
        """
        return self._username

    @username.setter
    def username(self, value: str | None) -> None:
        """Set the URL username.

        :param value: The URL username.
        """
        if value is None:
            self._username = None
        else:
            self._username = str(value)

    @property
    def password(self) -> str | None:
        """Get the URL password.

        :return: The URL password.
        """
        return self._password

    @password.setter
    def password(self, value: str | None) -> None:
        """Set the URL password.

        :param value: The URL password.
        """
        if value is None:
            self._password = None
        else:
            self._password = str(value)

    @property
    def host(self) -> str | None:
        """Get the URL host.

        :return: The URL host.
        """
        return self._host

    @host.setter
    def host(self, value: str | None) -> None:
        """Set the URL host.

        :param value: The URL host.
        """
        if value and not isinstance(value, str):
            raise TypeError(f"Host: Expected str or None, got {type(value)}")

        self._host = value

    @property
    def port(self) -> int | str | None:
        """Get the URL port.

        :return: The URL port as an Int if set, or None otherwise.
        """
        return self._port

    @port.setter
    def port(self, value: int | str | None) -> None:
        """Set the URL port.

        :param value: The URL port. This should be a number between 0 and 65535.

        :raises ValueError: If the port is not a valid integer.
        """
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
    def netloc(self) -> str | None:
        """Get the netloc as defined by RFC1808.

        :return: The netloc as defined by RFC1808.
        """
        output = ""

        if self.username:
            output += self.username

            if self.password:
                output += f":{self.password}"

            output += "@"

        if self.host:
            output += self.host

        if self.port:
            output += f":{self.port}"

        if len(output) == 0:
            return None

        return output

    @property
    def path(self) -> HttpPath:
        """Get the URL path.

        :return: The URL path as a HttpPath object.
        """
        return self._path

    @path.setter
    def path(self, value: str | HttpPath | None) -> None:
        """Set the URL path.

        :param value: The URL path. This can be a string or a HttpPath object.
        """
        if value is None:
            self._path = HttpPath()
            return

        if isinstance(value, str):
            if value:
                if value.startswith("/"):
                    value = value[1:]
                self._path = HttpPath(value.split("/"))
            else:
                self._path = HttpPath()
            return

        if isinstance(value, HttpPath):
            self._path = value
            return

        raise TypeError(f"Path: Expected str or HttpPath, got {type(value)}")

    @property
    def query(self) -> QuerySet:
        """Get the URL query.

        :return: The URL query as a QuerySet object.
        """
        return self._query

    @query.setter
    def query(
        self, value: dict[str, QueryValue | str | int | float | bool] | str | QuerySet | None
    ) -> None:
        """Set the URL query.

        :param value: The URL query. This can be a dict, a string, or a QuerySet
                      object. If it is a dict, the values can be QueryValue, a
                      string, a number or a boolean.

        :raises TypeError: If the query is not a dict, a string, or a QuerySet.
        """

        if (
            value is not None
            and not isinstance(value, dict)
            and not isinstance(value, str)
            and not isinstance(value, QuerySet)
        ):
            raise TypeError(f"Query: Expected dict, str, or None, got {type(value)}")

        if value is None:
            self._query = QuerySet(self._query_options)
            return

        if isinstance(value, QuerySet):
            self._query = value
            self._query_options = value.options
            return

        if isinstance(value, dict):
            self._query = QuerySet(self._query_options)
            for q_key, q_value in value.items():
                if q_value is None:
                    self._query.set_none_value(q_key)
                elif isinstance(q_value, QueryValue):
                    self._query[q_key] = q_value
                else:
                    self._query[q_key] = QueryValue(q_value, encoded=False)
            return

        # If it's a string, we need to parse it into a dict.
        # This doesn't appear in an RFC as far as I can tell. There's hints of
        # it in the HTML spec for form encoded data, but nothing concrete.

        components = value.split(self.query_options.query_joiner)

        query_set = QuerySet(self._query_options)

        for component in components:
            key_value = component.split("=", maxsplit=1)

            key = decode_query_value(key_value[0], self.query_options)

            if len(key_value) == 1:
                query_set[key] = None
            else:
                query_set[key] = QueryValue(key_value[1], encoded=True)

        self._query = query_set

    @property
    def fragment(self) -> str | None:
        """Get the URL fragment.

        :return: The URL fragment.
        """
        return self._fragment

    @fragment.setter
    def fragment(self, value: str | None) -> None:
        """Set the URL fragment.

        :param value: The URL fragment.
        """

        if value is None:
            self._fragment = None
        else:
            self._fragment = str(value)

    @property
    def query_options(self) -> QueryOptions:
        """Get the URL query options.

        Note: This gives the same result as the query.options property.

        :return: The URL query options.
        """
        return self._query_options

    @query_options.setter
    def query_options(self, value: QueryOptions) -> None:
        """Set the URL query options.

        Note: This also sets the query.options property.

        :param value: The URL query options.

        :raises TypeError: If the query options are not a QueryOptions object.
        """

        if not isinstance(value, QueryOptions):
            raise TypeError(f"Query options: Expected QueryOptions got {type(value)}")

        self._query_options = value

        # In the case where we have already set a query, we need to give it the
        # new options.
        if hasattr(self, "_query"):
            getattr(self, "_query").options = value

    @classmethod
    def parse(cls, string: str, query_options: QueryOptions = QueryOptions()) -> "HttpUrl":
        """Parse a URL string into a URL object.

        :param string: The URL string to parse.
        :param query_options: The query options for the URL, defaults to an
                              empty QueryOptions object (with defaults).

        :return: The URL object.
        """

        return _parse_http_or_https_url(string, query_options)


def _parse_net_loc(net_loc: str) -> tuple[str | None, str | None, str | None, int | None]:
    """Parse a netloc into its components.

    :param net_loc: The netloc to parse.

    :return: A tuple containing the username, password, host, and port.
    """

    # Netloc is auth info, host, and port. RFC 1808 doesn't actually decompose
    # this into its components, but it's incredible useful, so we'll do it here.

    # According to the BNF grammar, there are can be no `@` characters in the
    # netloc. However, RFC 3986 section 3.2.1 specifies that a `@` separates the
    # user info from the host. So we'll use that.

    userinfo_index = net_loc.find("@")

    if userinfo_index != -1:
        userinfo = net_loc[:userinfo_index]
        host_and_port = net_loc[userinfo_index + 1 :]
    else:
        userinfo = None
        host_and_port = net_loc

    # If we have a userinfo, we still need to split into username and password (if
    # there is a password). RFC 3986 section 3.2.1 specifies that the _first_
    # `:` seen separates the username from the password
    if userinfo:
        password_index = userinfo.find(":")

        if password_index != -1:
            password = userinfo[password_index + 1 :]
            username = userinfo[:password_index]
        else:
            username = userinfo
            password = None
    else:
        username = None
        password = None

    # Now we need to get the port from the host_and_port if it is defined. RFC
    # 3986 section 3.2 gives a grammar that shows that the port comes after the
    # _last_ colon if it is specified. We can't use any other as IPv6 addresses
    # can contain colons.

    if ":" in host_and_port:
        port_index = host_and_port.rfind(":")
        port_string = host_and_port[port_index + 1 :]
        if len(port_string) == 0:
            port = None
        else:
            port = int(port_string)
        host = host_and_port[:port_index]
    else:
        host = host_and_port
        port = None

    return username, password, host, port


# pylint: disable=too-many-branches
def _parse_http_or_https_url(value: str, query_options: QueryOptions = QueryOptions()) -> HttpUrl:
    """Parse a HTTP or HTTPS URL.

    :param value: The URL string to parse.
    :param query_options: The query options for the URL, defaults to an
                          empty QueryOptions object (with defaults).

    :return: The URL object.
    """

    # This comes from https://datatracker.ietf.org/doc/html/rfc1808
    # The rules in the grammar must be applied in order, so we'll do that here.

    # Rule #1: URL         = ( absoluteURL | relativeURL ) [ "#" fragment ]

    # According to 2.4.1:
    # ```
    # If the parse string contains a crosshatch "#" character, then the
    # substring after the first (left-most) crosshatch "#" and up to the
    # end of the parse string is the <fragment> identifier.
    # ```
    # So we can just split on the first # and take the second part as the fragment

    fragment_index = value.find("#")

    if fragment_index != -1:
        fragment = value[fragment_index + 1 :]
        value = value[:fragment_index]
    else:
        fragment = None

    # We now have an absoluteURL or a relativeURL left. A relativeURL has no
    # scheme, and since we only care about HTTP and HTTPS we can ignore that and
    # assume there is a scheme and therefore this is an absoluteURL.

    # Rule #2: absoluteURL = generic-RL | ( scheme ":" *( uchar | reserved ) )

    # Rule #3: generic-RL  = scheme ":" relativeURL

    # If we combine these two, we get: absoluteURL = (scheme ":" relativeURL) | ( scheme ":" *( uchar | reserved ) )
    # Either way, we have a scheme, so let's get it out.

    # 2.4.2:
    # If the parse string contains a colon ":" after the first character
    # and before any characters not allowed as part of a scheme name (i.e.,
    # any not an alphanumeric, plus "+", period ".", or hyphen "-"), the
    # <scheme> of the URL is the substring of characters up to but not
    # including the first colon.  These characters and the colon are then
    # removed from the parse string before continuing.

    # We are specifically looking for `http:` or `https:` as the scheme, so can
    # just check for that.

    if value.startswith("http:"):
        scheme = "http"
        value = value[5:]
    elif value.startswith("https:"):
        scheme = "https"
        value = value[6:]
    else:
        raise ValueError("URL: Expected 'http://' or 'https://' prefix")

    assert scheme in ("http", "https")

    # We are now left with a relativeURL.

    # Rule 4: relativeURL = net_path | abs_path | rel_path
    # Rule 5: net_path    = "//" net_loc [ abs_path ]
    # Rule 6: abs_path    = "/"  rel_path
    # Rule 7: rel_path    = [ path ] [ ";" params ] [ "?" query ]

    # 2.4.3:
    # If the parse string begins with a double-slash "//", then the
    # substring of characters after the double-slash and up to, but not
    # including, the next slash "/" character is the network location/login
    # (<net_loc>) of the URL.  If no trailing slash "/" is present, the
    # entire remaining parse string is assigned to <net_loc>.  The double-
    # slash and <net_loc> are removed from the parse string before

    if value.startswith("//"):
        value = value[2:]
        next_slash_index = value.find("/")

        # If we don't find it, we take to the end of the string.
        if next_slash_index == -1:
            next_slash_index = len(value)

        net_loc = value[:next_slash_index]

        # RFC 1808 doesn't actually decompose the netloc into its components,
        # but RFC 3986 allows us to do so.
        username, password, host, port = _parse_net_loc(net_loc)
        value = value[next_slash_index:]
    else:
        username = None
        password = None
        host = None
        port = None

    # 2.4.4 states:
    # If the parse string contains a question mark "?" character, then the
    # substring after the first (left-most) question mark "?" and up to the
    # end of the parse string is the <query> information.  If the question
    # mark is the last character, or no question mark is present, then the
    # query information is empty.  The matched substring, including the
    # question mark character, is removed from the parse string before
    # continuing.

    # Therefore, we can find the first `?` and split on that.

    query_index = value.find("?")

    if query_index != -1:
        query: str | None = value[query_index + 1 :]
        if query is not None and len(query) == 0:
            query = None
        value = value[:query_index]
    else:
        query = None

    # 2.4.6 states that everything left (if anything) is the path.
    if value == "":
        path = None
    else:
        path = value

    return HttpUrl(
        scheme=scheme,  # type: ignore # We check this above
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
