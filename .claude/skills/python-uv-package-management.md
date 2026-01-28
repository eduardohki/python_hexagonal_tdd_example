# Python Package Management with uv

This skill provides guidance for managing Python projects using uv, a fast Python package and project manager.

## Overview

uv is a modern Python package manager that replaces pip, pip-tools, pipenv, poetry, and virtualenv. It's written in Rust and is significantly faster than traditional Python tooling.

## Core Concepts

### Always Use `uv run`

All commands should be prefixed with `uv run` to ensure they execute in the correct virtual environment with the right dependencies:

```bash
uv run pytest              # Run tests
uv run ruff check src      # Run linter
uv run mypy src            # Run type checker
uv run python script.py    # Run a script
```

This eliminates the need to manually activate virtual environments.

### Project Initialization

```bash
# Create a new project
uv init my-project

# Create with src layout
uv init my-project --lib
```

## pyproject.toml Configuration

### Basic Project Metadata

```toml
[project]
name = "my-app"
version = "0.1.0"
description = "A Python application"
readme = "README.md"
requires-python = ">=3.12"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Dependencies

```toml
[project]
dependencies = [
    "requests>=2.28.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
]
```

### Dependency Groups (uv-specific)

```toml
[dependency-groups]
dev = [
    "ruff>=0.4.0",
    "mypy>=1.10.0",
    "pytest>=8.0.0",
]
test = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
]
```

### Scripts

```toml
[project.scripts]
my-cli = "my_app.cli:main"
```

### src Layout Configuration

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/my_app"]
```

## Common Commands

### Dependency Management

```bash
# Sync dependencies (install/update to match lock file)
uv sync

# Add a dependency
uv add requests

# Add a dev dependency
uv add --dev pytest

# Add to a specific group
uv add --group test pytest-cov

# Remove a dependency
uv remove requests

# Update all dependencies
uv lock --upgrade

# Update a specific dependency
uv lock --upgrade-package requests
```

### Running Commands

```bash
# Run a command in the virtual environment
uv run python -c "print('hello')"

# Run a module
uv run python -m pytest

# Run a script
uv run my-script.py

# Run with specific Python version
uv run --python 3.12 pytest
```

### Virtual Environment

```bash
# Create a virtual environment (usually automatic)
uv venv

# Create with specific Python version
uv venv --python 3.12

# The venv is created in .venv/ by default
```

### Python Version Management

```bash
# Install a Python version
uv python install 3.12

# List available Python versions
uv python list

# Pin Python version for project
uv python pin 3.12
```

## Lock File

uv generates a `uv.lock` file that:
- Locks all dependency versions for reproducibility
- Should be committed to version control
- Is cross-platform by default

```bash
# Generate/update lock file
uv lock

# Sync environment to match lock file
uv sync
```

## Project Structure

Recommended structure for a uv-managed project:

```
my-project/
├── .python-version         # Pinned Python version
├── .venv/                  # Virtual environment (gitignored)
├── pyproject.toml          # Project configuration
├── uv.lock                 # Lock file (committed)
├── src/
│   └── my_app/
│       └── __init__.py
└── tests/
    └── test_example.py
```

## Migration from Other Tools

### From pip + requirements.txt

```bash
# Import from requirements.txt
uv add -r requirements.txt

# Import dev requirements
uv add --dev -r requirements-dev.txt
```

### From Poetry

Most `pyproject.toml` fields are compatible. Main changes:
- Replace `[tool.poetry.dependencies]` with `[project.dependencies]`
- Replace `[tool.poetry.group.dev.dependencies]` with `[dependency-groups]`
- Remove poetry-specific sections

### From Pipenv

```bash
# uv can read Pipfile
uv add -r Pipfile
```

## Best Practices

### Do

- Always use `uv run` for executing commands
- Commit `uv.lock` to version control
- Use dependency groups to organize dev dependencies
- Use `uv sync` to ensure environment matches lock file
- Pin Python version with `.python-version` file

### Don't

- Never use `pip install` directly — use `uv add`
- Never modify `.venv/` manually
- Don't forget to run `uv sync` after pulling changes
- Don't ignore the lock file in version control

## Common Workflows

### Starting a New Feature

```bash
git checkout -b feature/my-feature
uv sync                    # Ensure environment is up to date
uv run pytest              # Verify tests pass
# ... make changes ...
uv run pytest              # Run tests again
```

### Adding a New Dependency

```bash
uv add new-package         # Add and update lock file
uv run pytest              # Verify nothing broke
git add pyproject.toml uv.lock
git commit -m "Add new-package dependency"
```

### Updating Dependencies

```bash
uv lock --upgrade          # Update all dependencies
uv sync                    # Apply updates
uv run pytest              # Verify nothing broke
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Install uv
  uses: astral-sh/setup-uv@v4

- name: Install dependencies
  run: uv sync

- name: Run tests
  run: uv run pytest
```

## Comparison with Other Tools

| Feature | uv | pip | poetry | pipenv |
|---------|-----|-----|--------|--------|
| Speed | ⚡ Very fast | Slow | Medium | Slow |
| Lock file | ✅ | ❌ | ✅ | ✅ |
| Built-in venv | ✅ | ❌ | ✅ | ✅ |
| pyproject.toml | ✅ | Partial | ✅ | ❌ |
| Python management | ✅ | ❌ | ❌ | ❌ |
