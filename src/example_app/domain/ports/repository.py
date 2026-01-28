"""
Repository port - Interface for data persistence operations.

This is an output (driven) port that defines how the domain layer
expects to interact with data storage systems.

Implementations of this interface (adapters) handle the actual
persistence logic (e.g., PostgreSQL, MongoDB, in-memory).
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

# Generic type for entities
T = TypeVar("T")
ID = TypeVar("ID")


class Repository(ABC, Generic[T, ID]):
    """Abstract base repository defining standard CRUD operations.

    This interface should be implemented by outbound adapters that
    handle actual data persistence.

    Type Parameters:
        T: The entity type this repository manages
        ID: The type of the entity's identifier
    """

    @abstractmethod
    def save(self, entity: T) -> T:
        """Persist an entity.

        Args:
            entity: The entity to save

        Returns:
            The saved entity (may include generated fields like ID)
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, entity_id: ID) -> T | None:
        """Find an entity by its identifier.

        Args:
            entity_id: The unique identifier of the entity

        Returns:
            The entity if found, None otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[T]:
        """Retrieve all entities.

        Returns:
            A list of all entities
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity_id: ID) -> bool:
        """Delete an entity by its identifier.

        Args:
            entity_id: The unique identifier of the entity to delete

        Returns:
            True if the entity was deleted, False if not found
        """
        raise NotImplementedError

    @abstractmethod
    def exists(self, entity_id: ID) -> bool:
        """Check if an entity exists.

        Args:
            entity_id: The unique identifier to check

        Returns:
            True if the entity exists, False otherwise
        """
        raise NotImplementedError
