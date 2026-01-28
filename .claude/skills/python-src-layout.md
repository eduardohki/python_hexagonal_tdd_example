# Python src Layout Convention

This skill provides guidance for organizing Python projects using the src layout convention.

## Overview

The src layout places all package code inside a `src/` directory, separating it from configuration files, tests, and other project artifacts. This structure prevents common import issues and ensures packages are properly installed before use.

## Project Structure

```
my-project/
├── src/
│   └── my_app/
│       ├── __init__.py
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── models/
│       │   └── use_cases/
│       └── adapters/
│           ├── __init__.py
│           ├── inbound/
│           └── outbound/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── domain/
├── pyproject.toml
├── README.md
└── uv.lock
```

## Why Use src Layout

### Problem with Flat Layout

In a flat layout, the package is in the project root:

```
my-project/
├── my_app/          # Package directly in root
│   └── __init__.py
├── tests/
└── pyproject.toml
```

This causes problems:

1. **Accidental imports**: Python can import from the local directory instead of the installed package
2. **Testing uninstalled code**: Tests might pass locally but fail after installation
3. **Import confusion**: `import my_app` might import the local folder, not the installed package

### src Layout Solves These Issues

With src layout:

1. **Forces installation**: You must install the package to import it
2. **Tests installed code**: Tests run against the installed version
3. **Clear separation**: Source code is isolated from project files

## Configuration

### pyproject.toml for Hatchling

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-app"
version = "0.1.0"

[tool.hatch.build.targets.wheel]
packages = ["src/my_app"]
```

### pyproject.toml for Setuptools

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-app"
version = "0.1.0"

[tool.setuptools.packages.find]
where = ["src"]
```

### pytest Configuration

Configure pytest to find your source code:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

The `pythonpath = ["src"]` setting allows pytest to import from `src/` without installing the package in editable mode.

### Mypy Configuration

Tell mypy where to find your code:

```toml
[tool.mypy]
python_version = "3.12"
mypy_path = "src"
```

## Imports

### Internal Imports

Always use absolute imports from the package root:

```python
# src/my_app/domain/use_cases/create_user.py

# Correct - absolute import from package
from my_app.domain.models.user import User
from my_app.domain.ports.repository import Repository

# Avoid - relative imports (harder to understand)
from ..models.user import User
from ..ports.repository import Repository
```

### Test Imports

Tests import from the installed package:

```python
# tests/domain/use_cases/test_create_user.py

from my_app.domain.use_cases.create_user import CreateUserUseCase
from my_app.domain.models.user import User
```

## Package Naming

### Directory vs Package Name

The directory name should match the package name, using underscores:

```
src/
└── my_app/          # Package name: my_app
    └── __init__.py
```

The project name in `pyproject.toml` can use hyphens:

```toml
[project]
name = "my-app"      # Project name (for pip install)
```

### Import Name

Users import using the package (directory) name:

```python
import my_app
from my_app.domain.models import User
```

## Development Workflow

### Installing for Development

With uv, dependencies are automatically synced:

```bash
# Install dependencies (creates .venv if needed)
uv sync
```

### Running Commands

Use `uv run` to execute in the virtual environment:

```bash
uv run pytest
uv run mypy src
uv run python -c "from my_app import __version__; print(__version__)"
```

### Editable Installation

For development, the package is installed in editable mode automatically by uv. This means changes to source files are immediately reflected without reinstalling.

## __init__.py Files

### Root Package __init__.py

```python
# src/my_app/__init__.py
"""My Application - A hexagonal architecture example."""

__version__ = "0.1.0"
```

### Subpackage __init__.py

Keep them minimal or empty:

```python
# src/my_app/domain/__init__.py
"""Domain layer containing business logic."""
```

### Re-exporting for Convenience

Optionally re-export key classes:

```python
# src/my_app/domain/models/__init__.py
"""Domain models."""

from my_app.domain.models.user import User
from my_app.domain.models.order import Order

__all__ = ["User", "Order"]
```

This allows:

```python
from my_app.domain.models import User
# Instead of:
from my_app.domain.models.user import User
```

## Common Patterns

### Version in __init__.py

```python
# src/my_app/__init__.py
__version__ = "0.1.0"
```

Access programmatically:

```python
import my_app
print(my_app.__version__)
```

### Package-Level Exports

```python
# src/my_app/__init__.py
"""My Application."""

__version__ = "0.1.0"

from my_app.domain.models.user import User
from my_app.domain.use_cases.create_user import CreateUserUseCase

__all__ = [
    "__version__",
    "User",
    "CreateUserUseCase",
]
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'my_app'"

1. Ensure `pythonpath = ["src"]` is set in `pyproject.toml` for pytest
2. Run commands with `uv run` to use the correct environment
3. Check that `src/my_app/__init__.py` exists

### Tests Import Wrong Version

If tests import from a different location:

1. Remove any `my_app` directory outside of `src/`
2. Clear `__pycache__` directories: `find . -type d -name __pycache__ -exec rm -rf {} +`
3. Reinstall: `uv sync`

### IDE Not Finding Imports

Configure your IDE to recognize `src/` as a source root:

- **VS Code**: Add `"python.analysis.extraPaths": ["src"]` to settings
- **PyCharm**: Right-click `src/` → Mark Directory as → Sources Root

## Do

- Place all package code under `src/`
- Use absolute imports from the package root
- Configure `pythonpath = ["src"]` for pytest
- Keep `__init__.py` files minimal
- Use underscores in package names (`my_app`)

## Don't

- Don't put package code directly in the project root
- Don't use relative imports (prefer absolute)
- Don't forget `__init__.py` files in packages
- Don't mix source code with tests or config files
- Don't manually modify `sys.path` in source code
