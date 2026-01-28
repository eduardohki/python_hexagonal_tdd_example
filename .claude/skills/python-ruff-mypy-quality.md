# Python Code Quality with Ruff and Mypy

This skill provides guidance for maintaining code quality in Python projects using Ruff for linting/formatting and Mypy for static type checking.

## Overview

- **Ruff**: An extremely fast Python linter and formatter written in Rust. Replaces flake8, isort, black, and many other tools.
- **Mypy**: A static type checker for Python that helps catch type-related bugs before runtime.

## Ruff

### Running Ruff

```bash
# Check for linting issues
uv run ruff check src tests

# Check and automatically fix issues
uv run ruff check --fix src tests

# Format code (like Black)
uv run ruff format src tests

# Check formatting without making changes
uv run ruff format --check src tests
```

### pyproject.toml Configuration

```toml
[tool.ruff]
target-version = "py312"
line-length = 88
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
]
ignore = [
    "E501",   # line too long (handled by formatter)
]

[tool.ruff.lint.isort]
known-first-party = ["my_app"]

[tool.ruff.lint.per-file-ignores]
"tests/**/*" = ["ARG"]  # Allow unused arguments in tests (fixtures)
```

### Common Rule Sets

| Code | Plugin | Description |
|------|--------|-------------|
| `E`, `W` | pycodestyle | PEP 8 style violations |
| `F` | Pyflakes | Logical errors (undefined names, unused imports) |
| `I` | isort | Import sorting |
| `B` | flake8-bugbear | Common bugs and design problems |
| `C4` | flake8-comprehensions | Better comprehensions |
| `UP` | pyupgrade | Upgrade syntax for newer Python |
| `SIM` | flake8-simplify | Simplify code |
| `ARG` | flake8-unused-arguments | Unused function arguments |
| `PTH` | flake8-use-pathlib | Prefer pathlib over os.path |
| `RUF` | Ruff-specific | Ruff's own rules |

### Ignoring Rules

```python
# Ignore specific rule on a line
x = 1  # noqa: F841

# Ignore multiple rules
x = 1  # noqa: F841, E501

# Ignore all rules on a line
x = 1  # noqa

# File-level ignore (at top of file)
# ruff: noqa: F401
```

### Formatting Style

Ruff's formatter is designed to be a drop-in replacement for Black:

- 88 characters line length (configurable)
- Double quotes for strings
- Trailing commas in multi-line structures
- Consistent indentation

## Mypy

### Running Mypy

```bash
# Type check source code
uv run mypy src

# Type check with verbose output
uv run mypy src --verbose

# Type check specific file
uv run mypy src/my_app/module.py

# Generate HTML report
uv run mypy src --html-report mypy-report
```

### pyproject.toml Configuration

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true

# Per-module configuration
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[[tool.mypy.overrides]]
module = "third_party_lib.*"
ignore_missing_imports = true
```

### Strict Mode

`strict = true` enables all of these:

- `disallow_untyped_defs`: Functions must have type annotations
- `disallow_incomplete_defs`: Partial annotations not allowed
- `check_untyped_defs`: Type check inside untyped functions
- `disallow_untyped_decorators`: Decorators must be typed
- `no_implicit_optional`: `None` must be explicit in `Optional`
- `warn_return_any`: Warn when returning `Any`
- `warn_unused_ignores`: Warn on unnecessary `# type: ignore`

### Type Hints Cheat Sheet

```python
from typing import Any, TypeVar, Generic
from collections.abc import Callable, Iterable, Sequence

# Basic types
def greet(name: str) -> str:
    return f"Hello, {name}"

# Optional (can be None)
def find(id: int) -> User | None:
    ...

# Collections
def process(items: list[str]) -> dict[str, int]:
    ...

# Union types
def parse(value: str | int) -> str:
    ...

# Callable
def apply(func: Callable[[int, int], int], a: int, b: int) -> int:
    return func(a, b)

# TypeVar for generics
T = TypeVar("T")

def first(items: Sequence[T]) -> T | None:
    return items[0] if items else None

# Generic classes
class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value
```

### Ignoring Type Errors

```python
# Ignore specific error on a line
result = some_untyped_function()  # type: ignore[no-untyped-call]

# Ignore all errors on a line (avoid when possible)
result = problematic_code()  # type: ignore

# Cast when you know better than mypy
from typing import cast
value = cast(str, get_unknown_value())

# Assert for type narrowing
assert isinstance(value, str)
```

### Common Type Patterns

#### Protocol for Structural Typing

```python
from typing import Protocol

class Readable(Protocol):
    def read(self) -> str: ...

def process(source: Readable) -> str:
    return source.read()
```

#### TypedDict for Dictionaries

```python
from typing import TypedDict

class UserDict(TypedDict):
    name: str
    age: int
    email: str | None
```

#### Literal for Specific Values

```python
from typing import Literal

def set_mode(mode: Literal["read", "write", "append"]) -> None:
    ...
```

## Combined Workflow

### Pre-commit Checks

Run all quality checks before committing:

```bash
# Full quality check pipeline
uv run ruff check src tests && \
uv run ruff format src tests && \
uv run mypy src
```

### CI Configuration

```yaml
# GitHub Actions example
- name: Lint
  run: uv run ruff check src tests

- name: Format check
  run: uv run ruff format --check src tests

- name: Type check
  run: uv run mypy src
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies: []
```

## Do

- Run `ruff check` and `ruff format` before every commit
- Use strict mode in mypy for new projects
- Add type hints to all function signatures
- Use `# type: ignore[specific-error]` with specific error codes
- Configure per-file ignores for tests when needed
- Use modern type syntax (`list[str]` not `List[str]`, `X | None` not `Optional[X]`)

## Don't

- Don't use bare `# type: ignore` without error codes
- Don't use bare `# noqa` without rule codes
- Don't disable rules globally when per-file ignores work
- Don't ignore type errors without understanding them
- Don't use `Any` as an escape hatch for complex types
- Don't skip type checking on new code
