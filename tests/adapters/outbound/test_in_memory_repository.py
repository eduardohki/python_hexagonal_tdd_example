"""
Integration tests for InMemoryExampleEntityRepository.

These tests verify that the in-memory repository correctly satisfies
the ExampleEntityRepository protocol and behaves as expected.
"""

import pytest

from example_app.adapters.outbound.in_memory_repository import (
    InMemoryExampleEntityRepository,
)
from example_app.domain.models.example_entity import ExampleEntity
from example_app.domain.ports.repository import ExampleEntityRepository


@pytest.fixture
def repository() -> ExampleEntityRepository:
    """Provide a fresh in-memory repository for each test.

    Return type is the Protocol, not the concrete class.
    This ensures the adapter satisfies the protocol contract.
    """
    return InMemoryExampleEntityRepository()


@pytest.fixture
def sample_entity() -> ExampleEntity:
    """Provide a sample entity for testing."""
    return ExampleEntity.create(
        name="Test Entity",
        description="A test entity for integration tests",
    )


@pytest.mark.integration
class TestInMemoryExampleEntityRepository:
    """Integration tests for the InMemoryExampleEntityRepository adapter."""

    def test_save_and_find_by_id(
        self,
        repository: ExampleEntityRepository,
        sample_entity: ExampleEntity,
    ) -> None:
        """Should save an entity and retrieve it by ID."""
        saved = repository.save(sample_entity)

        found = repository.find_by_id(sample_entity.id)

        assert found is not None
        assert found.id == sample_entity.id
        assert found.name == sample_entity.name
        assert saved == found

    def test_find_by_id_not_found(
        self,
        repository: ExampleEntityRepository,
    ) -> None:
        """Should return None when entity is not found."""
        from uuid import uuid4

        result = repository.find_by_id(uuid4())

        assert result is None

    def test_find_all_empty(
        self,
        repository: ExampleEntityRepository,
    ) -> None:
        """Should return empty list when no entities exist."""
        result = repository.find_all()

        assert result == []

    def test_find_all_with_entities(
        self,
        repository: ExampleEntityRepository,
    ) -> None:
        """Should return all saved entities."""
        entity1 = ExampleEntity.create(name="Entity 1")
        entity2 = ExampleEntity.create(name="Entity 2")
        repository.save(entity1)
        repository.save(entity2)

        result = repository.find_all()

        assert len(result) == 2
        assert entity1 in result
        assert entity2 in result

    def test_delete_existing_entity(
        self,
        repository: ExampleEntityRepository,
        sample_entity: ExampleEntity,
    ) -> None:
        """Should delete an existing entity and return True."""
        repository.save(sample_entity)

        deleted = repository.delete(sample_entity.id)

        assert deleted is True
        assert repository.find_by_id(sample_entity.id) is None

    def test_delete_non_existing_entity(
        self,
        repository: ExampleEntityRepository,
    ) -> None:
        """Should return False when trying to delete non-existing entity."""
        from uuid import uuid4

        deleted = repository.delete(uuid4())

        assert deleted is False

    def test_exists_true(
        self,
        repository: ExampleEntityRepository,
        sample_entity: ExampleEntity,
    ) -> None:
        """Should return True for existing entity."""
        repository.save(sample_entity)

        result = repository.exists(sample_entity.id)

        assert result is True

    def test_exists_false(
        self,
        repository: ExampleEntityRepository,
    ) -> None:
        """Should return False for non-existing entity."""
        from uuid import uuid4

        result = repository.exists(uuid4())

        assert result is False

    def test_clear(
        self,
        repository: ExampleEntityRepository,
    ) -> None:
        """Should remove all entities from storage.

        Note: clear() is an adapter-specific method not part of the protocol.
        We check the instance type to access it.
        """
        entity1 = ExampleEntity.create(name="Entity 1")
        entity2 = ExampleEntity.create(name="Entity 2")
        repository.save(entity1)
        repository.save(entity2)

        # clear() is adapter-specific, not part of the protocol
        assert isinstance(repository, InMemoryExampleEntityRepository)
        repository.clear()

        assert repository.find_all() == []
        assert repository.exists(entity1.id) is False
        assert repository.exists(entity2.id) is False

    def test_save_updates_existing_entity(
        self,
        repository: ExampleEntityRepository,
        sample_entity: ExampleEntity,
    ) -> None:
        """Should update an existing entity when saved with same ID."""
        repository.save(sample_entity)
        updated_entity = sample_entity.update_name("Updated Name")

        repository.save(updated_entity)

        found = repository.find_by_id(sample_entity.id)
        assert found is not None
        assert found.name == "Updated Name"
        assert len(repository.find_all()) == 1
