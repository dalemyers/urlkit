# urlkit

Working with URLs in Python sucks. Until now.

Previously, the way to work with URLs was with `urllib`. This was always difficult to remember, and very verbose. For example, let's take a URL and change one of the query parameters:

```python
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

url_string = "http://example.com/?foo=bar&baz=qux"
# Parse the URL into components
parsed_url = urlparse(url_string)

# Parse the query string into a dictionary
query_params = parse_qs(parsed_url.query)

# Modify the specified query parameter
query_params[param] = [new_value]

# Reconstruct the query string
new_query = urlencode(query_params, doseq=True)

# Rebuild the URL with the updated query string
new_url = urlunparse((
    parsed_url.scheme,     # Scheme (e.g., http)
    parsed_url.netloc,     # Network location (e.g., example.com)
    parsed_url.path,       # Path (e.g., /)
    parsed_url.params,     # Parameters (if any)
    new_query,             # New query string
    parsed_url.fragment    # Fragment (if any)
))
```

Now with `urlkit`:

```python
from urlkit.http_url import HttpUrl

url_string = "http://example.com/?foo=bar&baz=qux"
# Parse the URL
url = HttpUrl.parse(url_string)

# Set the parameter
url.query["foo"] = "Hello"

# Generate the new URL
new_url = str(url)
```

The goal for `urlkit` is for everything to be simpler and easier.

## URL Type Support

The types in the table are intended to have eventual functionality. It shows which are currently supported.

| Type   | Supported | Notes                                                                                                                 |
| ------ | --------- | --------------------------------------------------------------------------------------------------------------------- |
| HTTP   | ✅        | More or less complete support following [RFC 1738](https://datatracker.ietf.org/doc/html/rfc1738) as far as possible. |
| HTTPS  | ✅        | More or less complete support following [RFC 1738](https://datatracker.ietf.org/doc/html/rfc1738) as far as possible. |
| FTP    | ❌        |                                                                                                                       |
| File   | ❌        |                                                                                                                       |
| Mailto | ❌        |                                                                                                                       |
| Telnet | ❌        |                                                                                                                       |

## Example Usage:

#### Constructing URLs

```python
url = HttpUrl(host="example.com", port=12345, query={"search_text": "Hello World"})
str(url) # http://example.com:12345/?search_text=Hello%20World

url = HttpUrl(host="example.com", query={"search_text": "Hello World"}, query_options=QueryOptions(space_encoding=SpaceEncoding.PLUS))
str(url) # http://example.com:12345/?search_text=Hello+World

url = HttpUrl(host="example.com", query="some%20pre-encoded%20text")
str(url) # http://example.com/?some%20pre-encoded%20text
```

#### Parsing URLs

```python
# Parsing a HTTP URL:
http_url = HttpUrl.parse("http://username:password@example.com/search?description=Some%20Text")
http_url.path # /search
http_url.query # {"description": "Some Text"}
http_url.password # password

# Parsing a HTTPS URL:
https_url = HttpsUrl.parse("https://username:password@example.com/search?description=Some%20Text")

# Parsing either (unknown):
http_or_https_url = parse_http_or_https_url("http://username:password@example.com/search?description=Some%20Text")
type(http_or_https_url) # <class 'urlkit.http_url.HttpUrl'> - Automatically returns the correct type
```

#### Modifying URLs

```python
url = HttpUrl.parse("http://example.com/foo/bar") # http://example.com/foo/bar
url.path.append_component("baz") # http://example.com/foo/bar/baz
url.path.append_component("one/two") # http://example.com/foo/bar/baz/one/two
url.path.pop_last() # http://example.com/foo/bar/baz/one
url.path.pop_last() # http://example.com/foo/bar/baz
url.path.pop_last() # http://example.com/foo/bar
url.path.extend(["baz", "one", "two"]) # http://example.com/foo/bar/baz/one/two
```

## Explicitly Non-Supported Features

#### Multiple Query Parameters With Same Key

URLs are old. They have a _lot_ of cruft, and it can make them difficult to work with. For example, many implementations, such as `urllib`, allow a query parameter to appear multiple times. So if you were to use the url `http://example.com/?param=1&param=2` and then tried to get the result for `param` you would get a list back: `["1", "2"]`. This can be nice. The downside though is that it means that every time you query for a parameter, even though they almost always appear just once, you get a list. i.e. `https://example.com/?param=1` returns `["1"]`.
