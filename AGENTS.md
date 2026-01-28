# AGENTS.md - Instructions for LLMs

This document provides guidance for AI assistants working on this codebase.

## Project Overview

This is a Python project following **Hexagonal Architecture** (Ports and Adapters) with **Test-Driven Development** practices.

## Architecture Decisions

### Folder Structure

```
src/example_app/
├── domain/                 # The Hexagon (core business logic)
│   ├── models/             # Entities and value objects
│   ├── ports/              # Interfaces (abstract base classes)
│   └── use_cases/          # Application-specific business rules
└── adapters/
    ├── inbound/            # Driving adapters (REST API, CLI, etc.)
    └── outbound/           # Driven adapters (repositories, external APIs)
```

### Key Principles

1. **Use cases belong inside the domain** - Not in a separate application layer. The domain folder represents the entire hexagon.

2. **Dependencies point inward** - Adapters depend on ports, never the reverse. Domain has no external dependencies.

3. **Ports are interfaces** - Defined as abstract base classes (ABCs) in `domain/ports/`. Adapters implement these interfaces.

4. **src layout** - Code lives in `src/example_app/` to ensure proper package installation and avoid import confusion.

## Testing Practices

### Test Organization

Tests mirror the source structure and use **pytest markers** for categorization:

```
tests/
├── domain/
│   ├── models/
│   ├── ports/
│   └── use_cases/          # Unit tests go here (@pytest.mark.unit)
└── adapters/
    ├── inbound/
    └── outbound/           # Integration tests (@pytest.mark.integration)
```

### Unit Tests

- **Unit tests are for use cases**, not models
- Use `pytestmark = pytest.mark.unit` at the top of test modules
- Use **fake implementations** of ports (not mocks) for testing use cases in isolation
- Test behavior, not implementation details

### BDD-Style Test Naming

Use the `given_when_then` pattern for test method names:

```python
def test_given_valid_input_when_create_entity_then_entity_is_persisted(self):
    # Given
    use_case = CreateEntityUseCase(repository=fake_repository)
    input_data = CreateEntityInput(name="Test")

    # When
    result = use_case.execute(input_data)

    # Then
    assert result.id is not None
    assert fake_repository.exists(result.id)
```

### Integration Tests

- Use `pytestmark = pytest.mark.integration` at the top of test modules
- Test adapters with real (or realistic) external dependencies
- Located in `tests/adapters/`

### Running Tests

```bash
uv run pytest                  # All tests
uv run pytest -m unit          # Only unit tests
uv run pytest -m integration   # Only integration tests
uv run pytest tests/domain     # By path
uv run pytest --cov=example_app --cov-report=html  # With coverage
```

## Python Best Practices

### Code Style

- Follow PEP 8
- Use type hints for all function signatures
- Use dataclasses for domain models
- Prefer immutability where possible

### Pre-commit Checks

Before committing, ensure:

1. **Linting passes**:
   ```bash
   uv run ruff check src tests
   ```

2. **Formatting is correct**:
   ```bash
   uv run ruff format src tests
   ```

3. **Type checking passes**:
   ```bash
   uv run mypy src
   ```

4. **All tests pass**:
   ```bash
   uv run pytest
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

## Package Management

This project uses `pyproject.toml` for configuration.

Since `pythonpath = ["src"]` is configured in `pyproject.toml`, you can run tests without installing the package:

```bash
uv run pytest
```
