# Python Test-Driven Development with pytest

This skill provides guidance for Test-Driven Development practices using pytest in Python projects.

## TDD Workflow

Follow Red-Green-Refactor:

1. **Red**: Write a failing test that defines expected behavior
2. **Green**: Write the minimum code to make the test pass
3. **Refactor**: Improve the code while keeping tests green

Always write tests before implementation.

## Test Organization

Tests should mirror the source structure:

```
tests/
├── conftest.py             # Shared fixtures
├── domain/
│   ├── models/
│   ├── ports/
│   └── use_cases/          # Unit tests (@pytest.mark.unit)
└── adapters/
    ├── inbound/
    └── outbound/           # Integration tests (@pytest.mark.integration)
```

## Test Markers

Use pytest markers to categorize tests:

- `@pytest.mark.unit` - Fast, isolated tests with no external dependencies
- `@pytest.mark.integration` - Tests that may require external systems

Configure markers in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests - fast, isolated, no external dependencies",
    "integration: Integration tests - may require external dependencies",
]
```

## BDD-Style Test Naming

Use the `given_when_then` pattern for test method names:

```python
import pytest


@pytest.mark.unit
class TestCreateEntityUseCase:
    def test_given_valid_input_when_create_entity_then_entity_is_persisted(
        self, fake_repository: FakeRepository
    ) -> None:
        # Given
        use_case = CreateEntityUseCase(repository=fake_repository)
        input_data = CreateEntityInput(name="Test")

        # When
        result = use_case.execute(input_data)

        # Then
        assert result.id is not None
        assert fake_repository.exists(result.id)

    def test_given_empty_name_when_create_entity_then_raises_validation_error(
        self, fake_repository: FakeRepository
    ) -> None:
        # Given
        use_case = CreateEntityUseCase(repository=fake_repository)
        input_data = CreateEntityInput(name="")

        # When / Then
        with pytest.raises(ValidationError):
            use_case.execute(input_data)
```

## Fake Implementations vs Mocks

Prefer fake implementations over mocks for testing. Fakes are simpler, more readable, and test behavior rather than implementation details.

### Fake Repository Example

```python
from uuid import UUID

from <app_name>.domain.models.entity import Entity


class FakeRepository:
    """Fake repository for testing use cases in isolation.
    
    No inheritance needed — this class satisfies the Repository[Entity, UUID]
    protocol through structural typing (duck typing with type safety).
    """

    def __init__(self) -> None:
        self._storage: dict[UUID, Entity] = {}

    def save(self, entity: Entity) -> Entity:
        self._storage[entity.id] = entity
        return entity

    def find_by_id(self, entity_id: UUID) -> Entity | None:
        return self._storage.get(entity_id)

    def find_all(self) -> list[Entity]:
        return list(self._storage.values())

    def delete(self, entity_id: UUID) -> bool:
        if entity_id in self._storage:
            del self._storage[entity_id]
            return True
        return False

    def exists(self, entity_id: UUID) -> bool:
        return entity_id in self._storage
```

## Fixtures

Define shared fixtures in `conftest.py`:

```python
import pytest

from <app_name>.domain.ports.repository import Repository
from tests.fakes import FakeRepository


@pytest.fixture
def fake_repository() -> Repository:
    """Provide a fake repository for testing.
    
    Return type is the Protocol, but the actual instance is a fake.
    This ensures the fake satisfies the protocol contract.
    """
    return FakeRepository()


@pytest.fixture
def app_config() -> dict:
    """Provide test application configuration."""
    return {
        "environment": "test",
        "debug": True,
    }
```

## Test Templates

### Unit Test for Use Case

```python
import pytest

from <app_name>.domain.use_cases.create_entity import CreateEntityUseCase, CreateEntityInput
from tests.fakes import FakeRepository


@pytest.fixture
def fake_repository() -> FakeRepository:
    return FakeRepository()


@pytest.mark.unit
class TestCreateEntityUseCase:
    def test_given_valid_input_when_execute_then_returns_created_entity(
        self, fake_repository: FakeRepository
    ) -> None:
        # Given
        use_case = CreateEntityUseCase(repository=fake_repository)
        input_data = CreateEntityInput(name="Test Entity")

        # When
        result = use_case.execute(input_data)

        # Then
        assert result.id is not None
        assert result.name == "Test Entity"

    def test_given_valid_input_when_execute_then_entity_is_persisted(
        self, fake_repository: FakeRepository
    ) -> None:
        # Given
        use_case = CreateEntityUseCase(repository=fake_repository)
        input_data = CreateEntityInput(name="Test Entity")

        # When
        result = use_case.execute(input_data)

        # Then
        assert fake_repository.exists(result.id)
```

### Integration Test for Adapter

```python
from uuid import UUID

import pytest

from <app_name>.adapters.outbound.in_memory_repository import InMemoryRepository
from <app_name>.domain.models.entity import Entity


@pytest.fixture
def repository() -> InMemoryRepository[Entity, UUID]:
    return InMemoryRepository()


@pytest.fixture
def sample_entity() -> Entity:
    return Entity.create(name="Test Entity", description="A test entity")


@pytest.mark.integration
class TestInMemoryRepository:
    def test_save_and_find_by_id(
        self,
        repository: InMemoryRepository[Entity, UUID],
        sample_entity: Entity,
    ) -> None:
        saved = repository.save(sample_entity)

        found = repository.find_by_id(sample_entity.id)

        assert found is not None
        assert found.id == sample_entity.id
        assert saved == found

    def test_find_by_id_returns_none_when_not_found(
        self,
        repository: InMemoryRepository[Entity, UUID],
    ) -> None:
        from uuid import uuid4

        result = repository.find_by_id(uuid4())

        assert result is None

    def test_delete_existing_entity_returns_true(
        self,
        repository: InMemoryRepository[Entity, UUID],
        sample_entity: Entity,
    ) -> None:
        repository.save(sample_entity)

        deleted = repository.delete(sample_entity.id)

        assert deleted is True
        assert repository.find_by_id(sample_entity.id) is None
```

## Running Tests

```bash
uv run pytest                  # All tests
uv run pytest -m unit          # Only unit tests
uv run pytest -m integration   # Only integration tests
uv run pytest tests/domain     # By path
uv run pytest -v               # Verbose output
uv run pytest -x               # Stop on first failure
uv run pytest --cov=<app_name> --cov-report=html  # With coverage
```

## pytest Configuration

Recommended `pyproject.toml` configuration:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
addopts = [
    "-v",
    "--tb=short",
]
markers = [
    "unit: Unit tests - fast, isolated, no external dependencies",
    "integration: Integration tests - may require external dependencies",
]

[tool.coverage.run]
source = ["src/<app_name>"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

## Common Tasks

### Adding a New Use Case Test

1. Create test file: `tests/domain/use_cases/test_<name>.py`
2. Write test class with `@pytest.mark.unit` decorator
3. Create fixtures for fakes
4. Write failing test with `given_when_then` naming
5. Implement use case until tests pass

### Adding a New Adapter Test

1. Create test file: `tests/adapters/outbound/test_<name>.py` (or `inbound/`)
2. Write test class with `@pytest.mark.integration` decorator
3. Create fixtures for the adapter and sample data
4. Write failing test
5. Implement adapter until tests pass

## Do

- Write tests before implementation (TDD)
- Use `@pytest.mark.unit` on test classes for use case tests
- Use `@pytest.mark.integration` on test classes for adapter tests
- Use fake implementations of ports for testing use cases
- Use `given_when_then` naming pattern for test methods
- Mirror test structure to source structure
- Add type hints to test functions
- Use fixtures for setup and dependency injection
- Let fakes satisfy protocols implicitly (no inheritance from ports)
- Type fixture return values as the Protocol, not the fake class

## Don't

- Don't use mocks when fakes are more appropriate
- Don't skip running tests after changes
- Don't test implementation details, test behavior
- Don't write tests that depend on each other
- Don't ignore test failures
- Don't make fakes inherit from port interfaces (use structural typing)
