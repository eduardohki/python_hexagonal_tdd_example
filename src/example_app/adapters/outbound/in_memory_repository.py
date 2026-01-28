"""
In-memory repository implementation.

This is an example outbound adapter that implements a repository port.
It stores data in memory and is useful for testing and prototyping.
"""

from typing import Generic, TypeVar

from example_app.domain.ports.repository import Repository

T = TypeVar("T")
ID = TypeVar("ID")


class InMemoryRepository(Repository[T, ID], Generic[T, ID]):
    """
    In-memory implementation of the Repository port.

    This adapter is useful for:
    - Unit testing use cases without a real database
    - Prototyping and development
    - Running the application without external dependencies
    """

    def __init__(self) -> None:
        self._storage: dict[ID, T] = {}

    def save(self, entity: T) -> T:
        """Save an entity to the in-memory storage."""
        entity_id = self._get_entity_id(entity)
        self._storage[entity_id] = entity
        return entity

    def find_by_id(self, entity_id: ID) -> T | None:
        """Retrieve an entity by its ID."""
        return self._storage.get(entity_id)

    def find_all(self) -> list[T]:
        """Retrieve all entities from the storage."""
        return list(self._storage.values())

    def delete(self, entity_id: ID) -> bool:
        """Delete an entity by its ID. Returns True if deleted, False if not found."""
        if entity_id in self._storage:
            del self._storage[entity_id]
            return True
        return False

    def exists(self, entity_id: ID) -> bool:
        """Check if an entity with the given ID exists."""
        return entity_id in self._storage

    def clear(self) -> None:
        """Clear all entities from storage. Useful for test cleanup."""
        self._storage.clear()

    def _get_entity_id(self, entity: T) -> ID:
        """
        Extract the ID from an entity.

        Override this method if your entities use a different ID attribute.
        """
        if hasattr(entity, "id"):
            return entity.id  # type: ignore
        raise ValueError(
            f"Entity {entity} does not have an 'id' attribute. "
            "Override _get_entity_id() to handle custom ID extraction."
        )
