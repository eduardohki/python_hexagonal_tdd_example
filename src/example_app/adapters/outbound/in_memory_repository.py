"""
In-memory repository implementation for ExampleEntity.

This is an example outbound adapter that satisfies the ExampleEntityRepository protocol.
It stores data in memory and is useful for testing and prototyping.

No inheritance from the port is needed — this class satisfies the protocol
through structural typing (duck typing with type safety).
"""

from uuid import UUID

from example_app.domain.models.example_entity import ExampleEntity


class InMemoryExampleEntityRepository:
    """
    In-memory adapter satisfying the ExampleEntityRepository protocol.

    This adapter is useful for:
    - Unit testing use cases without a real database
    - Prototyping and development
    - Running the application without external dependencies

    No inheritance from ExampleEntityRepository needed — just implement the methods.
    This class implicitly satisfies the protocol through structural typing.
    """

    def __init__(self) -> None:
        self._storage: dict[UUID, ExampleEntity] = {}

    def save(self, entity: ExampleEntity) -> ExampleEntity:
        """Save an entity to the in-memory storage."""
        self._storage[entity.id] = entity
        return entity

    def find_by_id(self, entity_id: UUID) -> ExampleEntity | None:
        """Retrieve an entity by its ID."""
        return self._storage.get(entity_id)

    def find_all(self) -> list[ExampleEntity]:
        """Retrieve all entities from the storage."""
        return list(self._storage.values())

    def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by its ID. Returns True if deleted, False if not found."""
        if entity_id in self._storage:
            del self._storage[entity_id]
            return True
        return False

    def exists(self, entity_id: UUID) -> bool:
        """Check if an entity with the given ID exists."""
        return entity_id in self._storage

    def clear(self) -> None:
        """Clear all entities from storage. Useful for test cleanup."""
        self._storage.clear()
