"""Example use case demonstrating the hexagonal architecture pattern.

Use cases contain application-specific business logic and orchestrate
the flow of data between the domain and the adapters through ports.
"""

from typing import Any

from example_app.domain.ports.repository import Repository


class ExampleUseCase:
    """Example use case demonstrating dependency injection through ports.

    This use case depends on an abstract repository (output port) which
    is injected at construction time. This allows for easy testing with
    mock/fake implementations and swapping implementations at runtime.
    """

    def __init__(self, repository: Repository[Any, Any]) -> None:
        """Initialize the use case with required dependencies.

        Args:
            repository: An implementation of the Repository port.
        """
        self._repository = repository

    def execute(self, input_data: str) -> str:
        """Execute the use case logic.

        Args:
            input_data: The input data for this use case.

        Returns:
            The result of the use case execution.
        """
        # Business logic goes here
        # This is where you orchestrate domain objects and call ports
        result = self._repository.save(input_data)
        return f"Processed: {result}"
