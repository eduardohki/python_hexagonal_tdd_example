"""
Repository port for ExampleEntity persistence.

This is an output (driven) port that defines how the domain layer
expects to interact with data storage for ExampleEntity.

Ports in hexagonal architecture are defined by use case needs,
not by generic CRUD patterns. Each entity type has its own
repository port with domain-specific methods.

Adapters satisfy this protocol through structural typing —
no inheritance required.
"""

from typing import Protocol
from uuid import UUID

from example_app.domain.models.example_entity import ExampleEntity


class ExampleEntityRepository(Protocol):
    """Repository protocol for ExampleEntity persistence.

    This port is defined by what the use cases need, not by
    generic data access patterns. Add methods here as use cases
    require them.

    Adapters satisfy this protocol by implementing these methods.
    No inheritance required — just implement the methods with matching signatures.
    """

    def save(self, entity: ExampleEntity) -> ExampleEntity:
        """Persist an entity.

        Args:
            entity: The entity to save

        Returns:
            The saved entity
        """
        ...

    def find_by_id(self, entity_id: UUID) -> ExampleEntity | None:
        """Find an entity by its identifier.

        Args:
            entity_id: The unique identifier of the entity

        Returns:
            The entity if found, None otherwise
        """
        ...

    def find_all(self) -> list[ExampleEntity]:
        """Retrieve all entities.

        Returns:
            A list of all entities
        """
        ...

    def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by its identifier.

        Args:
            entity_id: The unique identifier of the entity to delete

        Returns:
            True if the entity was deleted, False if not found
        """
        ...

    def exists(self, entity_id: UUID) -> bool:
        """Check if an entity exists.

        Args:
            entity_id: The unique identifier to check

        Returns:
            True if the entity exists, False otherwise
        """
        ...
