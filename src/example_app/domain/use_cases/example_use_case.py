"""Example use case demonstrating the hexagonal architecture pattern.

Use cases contain application-specific business logic and orchestrate
the flow of data between the domain and the adapters through ports.

Ports are defined by what the use case needs, not by generic CRUD patterns.
"""

from example_app.domain.models.example_entity import ExampleEntity
from example_app.domain.ports.repository import ExampleEntityRepository


class ExampleUseCase:
    """Example use case demonstrating dependency injection through ports.

    This use case depends on an ExampleEntityRepository (output port) which
    is injected at construction time. This allows for easy testing with
    fake implementations and swapping implementations at runtime.
    """

    def __init__(self, repository: ExampleEntityRepository) -> None:
        """Initialize the use case with required dependencies.

        Args:
            repository: An adapter satisfying the ExampleEntityRepository protocol.
        """
        self._repository = repository

    def execute(self, name: str, description: str | None = None) -> ExampleEntity:
        """Execute the use case logic.

        Args:
            name: The name for the new entity.
            description: Optional description for the entity.

        Returns:
            The created and persisted entity.
        """
        entity = ExampleEntity.create(name=name, description=description)
        return self._repository.save(entity)
