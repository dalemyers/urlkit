## Project Overview

**urlkit** is a Python library that simplifies URL manipulation. It provides an intuitive, Pythonic API for constructing, parsing, and modifying URLs, particularly HTTP(S) URLs.

## Design Patterns Used

- **Dataclasses**: Used for simple data containers (QueryOptions, QueryValue, HttpPathComponent)
- **ABC Pattern**: Base `URL` class for future protocol support
- **Type Safety**: Full type hints throughout, validated with mypy
- **Immutability where sensible**: QueryOptions uses frozen dataclass pattern
- **Early Return**: Return early rather than using if-else constructs where possible

## Development Guidelines

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
poetry run pytest --cov=urlkit --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_http_construction_paths.py -v

# Run with verbose output
python -m pytest -xvs
```

### Code Quality Checks

```bash
# Format code
poetry run black urlkit/ tests/

# Type checking
poetry run mypy urlkit/

# Linting
poetry run pylint urlkit/
```

## Testing Philosophy

- **Comprehensive Coverage**: Aim for 100% coverage
- **RFC Compliance**: Test against RFC examples where applicable
- **Type Safety**: Tests should catch type violations

## Future Improvement Ideas

These Pythonic improvements were identified but not yet implemented:

1. **PathLib-like API**: Add `/` operator for path joining
2. **Context Managers**: Builder pattern for incremental URL construction
3. **Descriptors**: Reduce property boilerplate with custom descriptors
4. **Protocol Classes**: Use `typing.Protocol` instead of empty ABC
5. **Cached Properties**: Use `@functools.cached_property` for expensive computations
6. **`__slots__`**: Add to HttpUrl for memory efficiency (if needed)

## Working with AI Agents

### Best Practices

1. **Run Tests Frequently**: After any change, run the test suite
2. **Check Type Hints**: Use mypy to verify type correctness
3. **Format Before Committing**: Always run black on modified files
4. **Maintain Coverage**: Don't decrease test coverage
5. **Document Changes**: Update docstrings when changing behavior

### Common Commands

## Notes for AI Agents

- This project values **clean, Pythonic code** over clever solutions
- **Type safety** is important - maintain all type hints
- **Test coverage** should remain at 100% ideally
- **RFC compliance** is important for URL handling
- **Backward compatibility** - don't break existing public APIs
- The project uses **Python 3.9+ features** (including `|` for Union types) - If you see something different, the user should be informed.

When making changes:
1. Understand the existing patterns first
2. Run tests before and after changes
3. Keep changes minimal and focused
4. Update documentation if behavior changes
5. Format code with black before completing
