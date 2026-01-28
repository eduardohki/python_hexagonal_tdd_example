"""
Example domain entity.

Domain entities represent core business concepts with identity.
They encapsulate business logic and are independent of any infrastructure concerns.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class ExampleEntity:
    """
    An example domain entity.

    Domain entities:
    - Have a unique identity (id)
    - Contain business logic related to their state
    - Are persistence-ignorant (no database-specific code)
    - Should be immutable or have controlled mutability

    Replace this with your actual domain entities.
    """

    id: UUID
    name: str
    description: Optional[str] = None

    @classmethod
    def create(cls, name: str, description: Optional[str] = None) -> "ExampleEntity":
        """
        Factory method to create a new entity with a generated ID.

        Args:
            name: The name of the entity
            description: Optional description

        Returns:
            A new ExampleEntity instance
        """
        return cls(
            id=uuid4(),
            name=name,
            description=description,
        )

    def update_name(self, new_name: str) -> "ExampleEntity":
        """
        Update the entity's name (immutable style - returns new instance).

        Args:
            new_name: The new name for the entity

        Returns:
            A new ExampleEntity instance with the updated name
        """
        return ExampleEntity(
            id=self.id,
            name=new_name,
            description=self.description,
        )

    def __eq__(self, other: object) -> bool:
        """Entities are equal if they have the same identity."""
        if not isinstance(other, ExampleEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on identity."""
        return hash(self.id)
