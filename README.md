# Python Hexagonal & TDD Example

A reference Python project for hexagonal architecture (ports and adapters) with Test-Driven Development.

## Project Structure

```
python_hexagonal_tdd_example/
├── src/
│   └── example_app/
│       ├── domain/                 # The hexagon (core business logic)
│       │   ├── models/             # Domain entities and value objects
│       │   │   └── example_entity.py
│       │   ├── ports/              # Interfaces (abstract base classes)
│       │   │   └── repository.py   # Output port for persistence
│       │   └── use_cases/          # Application-specific business rules
│       │       └── example_use_case.py
│       │
│       └── adapters/               # Infrastructure layer (outside the hexagon)
│           ├── inbound/            # Driving adapters (e.g., REST API, CLI)
│           └── outbound/           # Driven adapters (e.g., database, APIs)
│               └── in_memory_repository.py
│
├── tests/                          # Mirrors src structure, uses pytest markers
│   ├── conftest.py                 # Shared pytest fixtures
│   ├── domain/
│   │   ├── models/
│   │   ├── ports/
│   │   └── use_cases/
│   │       └── test_example_use_case.py  # @pytest.mark.unit
│   └── adapters/
│       ├── inbound/
│       └── outbound/
│           └── test_in_memory_repository.py  # @pytest.mark.integration
│
├── pyproject.toml                  # Project configuration
└── README.md
```

## Hexagonal Architecture Overview

```text
┌─────────────────┐   ┌──────────────────────────────────┐   ┌─────────────────┐
│                 │   │       Domain (The Hexagon)       │   │                 │
│ Inbound Adapters│   │ ┌────────┐ ┌──────┐ ┌─────────┐  │   │Outbound Adapters│
│                 │   │ │        │ │      │ │  Ports  │  │   │                 │
│ • REST API      │──▶│ │  Use   │─│Models│─│ (inter- │──│──▶│ • Repositories  │
│ • CLI           │   │ │ Cases  │ │      │ │ faces)  │  │   │ • External APIs │
│ • Message Queue │   │ └────────┘ └──────┘ └─────────┘  │   │ • Database      │
│                 │   │                                  │   │                 │
└─────────────────┘   └──────────────────────────────────┘   └─────────────────┘
   (adapters/                      (domain/)                     (adapters/
    inbound/)            models/ | use_cases/ | ports/             outbound/)
```

### Key Concepts

- **Domain Layer**: The hexagon containing pure business logic, entities, ports, and use cases. Has no dependencies on external frameworks or infrastructure.
- **Use Cases**: Application-specific business rules that orchestrate domain objects and coordinate with adapters through ports.
- **Ports**: Interfaces that define how the domain communicates with the outside world.
- **Adapters**: Implementations of ports that connect to external systems.

### Dependency Rule

Dependencies always point inward:
- Adapters depend on Ports
- Use Cases depend on Models and Ports
- Models have no external dependencies

## Installation

```bash
uv sync
```

## Running Tests

```bash
# Run all tests
pytest

# Run only unit tests (using markers)
pytest -m unit

# Run only integration tests (using markers)
pytest -m integration

# Run tests by path
pytest tests/domain
pytest tests/adapters

# Run with coverage
pytest --cov=example_app --cov-report=html
```

### Test Organization

Tests mirror the source structure and use **pytest markers** for categorization:

| Marker | Description | Example |
|--------|-------------|---------|
| `@pytest.mark.unit` | Fast, isolated, no external dependencies | Domain model tests |
| `@pytest.mark.integration` | May require external systems | Repository adapter tests |

Example:

```python
import pytest

@pytest.mark.unit
class TestMyEntity:
    def test_something(self):
        ...
```

## TDD Workflow

1. **Red**: Write a failing test that defines expected behavior
2. **Green**: Write the minimum code to make the test pass
3. **Refactor**: Improve the code while keeping tests green

## License

MIT
