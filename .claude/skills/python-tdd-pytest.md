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

Fakes should implement the **specific port** defined by the use case, not a generic repository:

```python
from uuid import UUID

from my_app.domain.models.user import User


class FakeUserRepository:
    """Fake repository for testing use cases in isolation.
    
    No inheritance needed — this class satisfies the UserRepository
    protocol through structural typing (duck typing with type safety).
    
    Implements only the methods the port defines (driven by use case needs).
    """

    def __init__(self) -> None:
        self._storage: dict[UUID, User] = {}

    def save(self, user: User) -> User:
        self._storage[user.id] = user
        return user

    def find_by_id(self, user_id: UUID) -> User | None:
        return self._storage.get(user_id)

    def find_by_email(self, email: str) -> User | None:
        for user in self._storage.values():
            if user.email == email:
                return user
        return None

    def exists_with_email(self, email: str) -> bool:
        return self.find_by_email(email) is not None
```

## Fixtures

Define shared fixtures in `conftest.py`:

```python
import pytest

from my_app.domain.ports.user_repository import UserRepository
from tests.fakes import FakeUserRepository


@pytest.fixture
def fake_user_repository() -> UserRepository:
    """Provide a fake repository for testing.
    
    Return type is the Protocol (UserRepository), not the fake class.
    This ensures the fake satisfies the protocol contract.
    """
    return FakeUserRepository()


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

from my_app.domain.use_cases.create_user import CreateUserUseCase, CreateUserInput
from my_app.domain.ports.user_repository import UserRepository
from tests.fakes import FakeUserRepository


@pytest.fixture
def fake_user_repository() -> UserRepository:
    return FakeUserRepository()


@pytest.mark.unit
class TestCreateUserUseCase:
    def test_given_valid_input_when_execute_then_returns_created_user(
        self, fake_user_repository: UserRepository
    ) -> None:
        # Given
        use_case = CreateUserUseCase(repository=fake_user_repository)
        input_data = CreateUserInput(name="John", email="john@example.com")

        # When
        result = use_case.execute(input_data)

        # Then
        assert result.id is not None
        assert result.name == "John"
        assert result.email == "john@example.com"

    def test_given_existing_email_when_execute_then_raises_error(
        self, fake_user_repository: UserRepository
    ) -> None:
        # Given
        use_case = CreateUserUseCase(repository=fake_user_repository)
        input_data = CreateUserInput(name="John", email="john@example.com")
        use_case.execute(input_data)  # Create first user

        # When / Then
        with pytest.raises(ValueError, match="already exists"):
            use_case.execute(CreateUserInput(name="Jane", email="john@example.com"))
```

### Integration Test for Adapter

```python
import pytest

from my_app.adapters.outbound.in_memory_user_repository import InMemoryUserRepository
from my_app.domain.models.user import User
from my_app.domain.ports.user_repository import UserRepository


@pytest.fixture
def repository() -> UserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def sample_user() -> User:
    return User.create(name="John", email="john@example.com")


@pytest.mark.integration
class TestInMemoryUserRepository:
    def test_save_and_find_by_id(
        self,
        repository: UserRepository,
        sample_user: User,
    ) -> None:
        saved = repository.save(sample_user)

        found = repository.find_by_id(sample_user.id)

        assert found is not None
        assert found.id == sample_user.id
        assert saved == found

    def test_find_by_email_returns_user(
        self,
        repository: UserRepository,
        sample_user: User,
    ) -> None:
        repository.save(sample_user)

        found = repository.find_by_email("john@example.com")

        assert found is not None
        assert found.email == "john@example.com"

    def test_exists_with_email_returns_true_for_existing(
        self,
        repository: UserRepository,
        sample_user: User,
    ) -> None:
        repository.save(sample_user)

        assert repository.exists_with_email("john@example.com") is True
        assert repository.exists_with_email("other@example.com") is False
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
- Create specific fakes for each port (e.g., `FakeUserRepository`, not generic `FakeRepository`)

## Don't

- Don't use mocks when fakes are more appropriate
- Don't skip running tests after changes
- Don't test implementation details, test behavior
- Don't write tests that depend on each other
- Don't ignore test failures
- Don't make fakes inherit from port interfaces (use structural typing)
- Don't create generic fakes — match the specific port's methods
