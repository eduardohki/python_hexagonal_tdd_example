# AGENTS.md - Instructions for AI Assistants

This document provides guidance for AI assistants working on this codebase.

## Quick Reference

Run after every change:

```bash
uv run ruff check src tests && uv run ruff format src tests && uv run mypy src && uv run pytest
```

## Project Overview

This is a Python project following **Hexagonal Architecture** (Ports and Adapters) with **Test-Driven Development** practices.

## Skills Reference

For detailed guidance on patterns and practices used in this project, see the skills in `.claude/skills/`:

| Skill | Description |
|-------|-------------|
| `python-hexagonal-architecture.md` | Architecture patterns, folder structure, ports and adapters |
| `python-tdd-pytest.md` | TDD workflow, test organization, BDD-style naming, fakes |
| `python-uv-package-management.md` | uv commands, dependency management, lock files |
| `python-ruff-mypy-quality.md` | Linting, formatting, type checking configuration |
| `python-dataclasses-modeling.md` | Domain entities, value objects, immutability patterns |
| `python-protocols-interfaces.md` | Protocols vs ABCs, composition over inheritance |
| `python-src-layout.md` | src layout convention, imports, package structure |
| `python-dependency-injection.md` | Constructor injection, composition root, testing with fakes |

## Tooling

| Tool | Purpose | Command prefix |
|------|---------|----------------|
| **uv** | Package manager and runner | `uv run` |
| **ruff** | Linting and formatting | `uv run ruff` |
| **mypy** | Static type checking | `uv run mypy` |
| **pytest** | Testing framework | `uv run pytest` |

Always use `uv run` to execute commands — this ensures the correct virtual environment and dependencies are used.

## Do

- Use `uv run` for all commands
- Add type hints to all functions
- Write tests before implementation (TDD)
- Use `@pytest.mark.unit` on test classes for use case tests
- Use `@pytest.mark.integration` on test classes for adapter tests
- Use fake implementations of ports for testing use cases
- Use `given_when_then` naming pattern for test methods
- Prefer Protocols over ABCs for interfaces
- Prefer composition over inheritance

## Don't

- Never import from `adapters/` inside `domain/`
- Never use `pip` directly — use `uv`
- Never skip running checks after changes
- Never put framework dependencies in `domain/`

## File Placement Rules

| Type | Location |
|------|----------|
| Entities / Value Objects | `src/example_app/domain/models/` |
| Port interfaces | `src/example_app/domain/ports/` |
| Use cases | `src/example_app/domain/use_cases/` |
| Inbound adapters | `src/example_app/adapters/inbound/` |
| Outbound adapters | `src/example_app/adapters/outbound/` |
| Tests | Mirror the source path under `tests/` |

## Common Tasks

### Adding a new use case

1. Create test file: `tests/domain/use_cases/test_<name>.py`
2. Write test class with `@pytest.mark.unit` decorator
3. Write failing test with `given_when_then` naming
4. Create use case: `src/example_app/domain/use_cases/<name>.py`
5. Implement until tests pass
6. Run checks: `uv run ruff check src tests && uv run ruff format src tests && uv run mypy src && uv run pytest`

### Adding a new adapter

1. Create test file: `tests/adapters/outbound/test_<name>.py` (or `inbound/`)
2. Write test class with `@pytest.mark.integration` decorator
3. Write failing test
4. Create adapter: `src/example_app/adapters/outbound/<name>.py`
5. Implement the port interface
6. Run checks

### Adding a new port

1. Create interface: `src/example_app/domain/ports/<name>.py`
2. Define Protocol (preferred) or ABC with `@abstractmethod` decorators
3. Run checks

## Running Tests

```bash
uv run pytest                  # All tests
uv run pytest -m unit          # Only unit tests
uv run pytest -m integration   # Only integration tests
uv run pytest tests/domain     # By path
uv run pytest --cov=example_app --cov-report=html  # With coverage
```

## When Making Changes

1. **Follow TDD** - Write failing tests first, then implement
2. **Keep the domain pure** - No framework dependencies in `domain/`
3. **Use ports for external communication** - Never call external systems directly from use cases
4. **Mirror test structure** - New source files should have corresponding test files
5. **Apply appropriate markers** - Use `@pytest.mark.unit` or `@pytest.mark.integration`
6. **Always run checks after making changes**:
   ```bash
   uv run ruff check src tests && uv run ruff format src tests && uv run mypy src && uv run pytest
   ```
