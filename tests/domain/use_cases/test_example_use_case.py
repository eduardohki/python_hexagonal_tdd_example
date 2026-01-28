"""
Unit tests for ExampleUseCase.

These tests verify the behavior of the use case in isolation,
using test doubles (fakes/mocks) for external dependencies (ports).

Uses BDD-style naming: given_<context>_when_<action>_then_<expected_outcome>
"""

from uuid import UUID

import pytest

from example_app.domain.models.example_entity import ExampleEntity
from example_app.domain.ports.repository import Repository

pytestmark = pytest.mark.unit


class FakeRepository(Repository[ExampleEntity, UUID]):
    """Fake repository for testing use cases in isolation."""

    def __init__(self) -> None:
        self._storage: dict[UUID, ExampleEntity] = {}

    def save(self, entity: ExampleEntity) -> ExampleEntity:
        self._storage[entity.id] = entity
        return entity

    def find_by_id(self, entity_id: UUID) -> ExampleEntity | None:
        return self._storage.get(entity_id)

    def find_all(self) -> list[ExampleEntity]:
        return list(self._storage.values())

    def delete(self, entity_id: UUID) -> bool:
        if entity_id in self._storage:
            del self._storage[entity_id]
            return True
        return False

    def exists(self, entity_id: UUID) -> bool:
        return entity_id in self._storage


@pytest.fixture
def fake_repository() -> FakeRepository:
    """Provide a fake repository for testing."""
    return FakeRepository()


class TestExampleUseCase:
    """Unit tests for ExampleUseCase.

    Example of what real use case tests might look like:

    def test_given_valid_input_when_create_entity_then_entity_is_persisted(
        self, fake_repository: FakeRepository
    ) -> None:
        # Given
        use_case = CreateEntityUseCase(repository=fake_repository)
        input_data = CreateEntityInput(name="Test", description="A test entity")

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
        input_data = CreateEntityInput(name="", description="Invalid entity")

        # When / Then
        with pytest.raises(ValidationError):
            use_case.execute(input_data)
    """

    def test_given_fake_repository_when_initialized_then_repository_is_available(
        self, fake_repository: FakeRepository
    ) -> None:
        # Given / When
        repository = fake_repository

        # Then
        assert repository is not None
