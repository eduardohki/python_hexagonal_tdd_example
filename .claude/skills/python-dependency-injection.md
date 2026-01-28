# Python Dependency Injection

This skill provides guidance for implementing dependency injection in Python applications, focusing on constructor injection and composition without DI frameworks.

## Overview

Dependency Injection (DI) is a design pattern where objects receive their dependencies from external sources rather than creating them internally. This promotes loose coupling, testability, and flexibility.

**Note**: This skill covers injecting *dependencies* (services, repositories, adapters). For creating *domain objects* (entities, value objects), see `python-dataclasses-modeling.md` which explains when to use constructors vs factory methods.

## Core Principles

### Inversion of Control

Instead of a class creating its dependencies, they are provided from outside:

```python
# Without DI - tightly coupled
class UserService:
    def __init__(self) -> None:
        self._repository = PostgresUserRepository()  # Hard-coded dependency
        self._emailer = SmtpEmailer()                # Hard-coded dependency


# With DI - loosely coupled
class UserService:
    def __init__(
        self,
        repository: Repository[User],
        emailer: Emailer,
    ) -> None:
        self._repository = repository
        self._emailer = emailer
```

### Depend on Abstractions

Classes should depend on interfaces (Protocols), not concrete implementations:

```python
from typing import Protocol


class Repository(Protocol[T]):
    def save(self, entity: T) -> T: ...
    def find_by_id(self, entity_id: UUID) -> T | None: ...


class Emailer(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...


class CreateUserUseCase:
    def __init__(
        self,
        repository: Repository[User],  # Depends on Protocol, not implementation
        emailer: Emailer,               # Depends on Protocol, not implementation
    ) -> None:
        self._repository = repository
        self._emailer = emailer
```

## Constructor Injection

The primary and preferred method of dependency injection in Python.

### Basic Pattern

```python
from typing import Protocol
from uuid import UUID


class Logger(Protocol):
    def info(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...


class OrderService:
    def __init__(
        self,
        repository: Repository[Order],
        payment_gateway: PaymentGateway,
        logger: Logger,
    ) -> None:
        self._repository = repository
        self._payment_gateway = payment_gateway
        self._logger = logger

    def place_order(self, order: Order) -> Order:
        self._logger.info(f"Placing order {order.id}")
        # ... business logic using injected dependencies
```

### With Default Implementations

Provide defaults for optional dependencies:

```python
class NullLogger:
    """No-op logger for when logging is not needed."""
    
    def info(self, message: str) -> None:
        pass

    def error(self, message: str) -> None:
        pass


class OrderService:
    def __init__(
        self,
        repository: Repository[Order],
        payment_gateway: PaymentGateway,
        logger: Logger | None = None,
    ) -> None:
        self._repository = repository
        self._payment_gateway = payment_gateway
        self._logger = logger or NullLogger()
```

## Composition Root

The composition root is where all dependencies are wired together. This should be at the application's entry point, outside the domain.

### Basic Composition Root

```python
# main.py or app.py - composition root
from my_app.adapters.outbound.postgres_repository import PostgresUserRepository
from my_app.adapters.outbound.smtp_emailer import SmtpEmailer
from my_app.adapters.outbound.console_logger import ConsoleLogger
from my_app.domain.use_cases.create_user import CreateUserUseCase


def create_application() -> Application:
    """Composition root - wire all dependencies here."""
    
    # Create adapters (concrete implementations)
    repository = PostgresUserRepository(connection_string="...")
    emailer = SmtpEmailer(host="smtp.example.com", port=587)
    logger = ConsoleLogger()
    
    # Create use cases with injected dependencies
    create_user_use_case = CreateUserUseCase(
        repository=repository,
        emailer=emailer,
        logger=logger,
    )
    
    # Create application with use cases
    return Application(
        create_user=create_user_use_case,
        # ... other use cases
    )


if __name__ == "__main__":
    app = create_application()
    app.run()
```

### Factory Functions

Use factory functions for creating adapters and wiring dependencies based on configuration. This is the most Pythonic approach for infrastructure concerns:

```python
def create_user_repository(config: Config) -> Repository[User]:
    """
    Factory function for creating repository adapter.
    
    Use factory FUNCTIONS (not methods) in the composition root
    for config-based adapter creation. This keeps infrastructure
    decisions out of domain classes.
    """
    if config.use_in_memory:
        return InMemoryRepository()
    return PostgresUserRepository(config.database_url)


def create_email_service(config: Config) -> Emailer:
    """Factory for email service based on configuration."""
    if config.environment == "test":
        return FakeEmailer()
    return SmtpEmailer(config.smtp_host, config.smtp_port)


def create_application(config: Config) -> Application:
    """Main composition root."""
    repository = create_user_repository(config)
    emailer = create_email_service(config)
    logger = create_logger(config)
    
    return Application(
        create_user=CreateUserUseCase(repository, emailer, logger),
        # ...
    )
```

## Hexagonal Architecture Integration

### Ports as Protocols

Define ports (interfaces) in the domain layer:

```python
# domain/ports/repository.py
from typing import Protocol, TypeVar
from uuid import UUID

T = TypeVar("T")


class Repository(Protocol[T]):
    """Output port for persistence."""
    
    def save(self, entity: T) -> T: ...
    def find_by_id(self, entity_id: UUID) -> T | None: ...
    def find_all(self) -> list[T]: ...
    def delete(self, entity_id: UUID) -> bool: ...
```

```python
# domain/ports/notification.py
from typing import Protocol


class NotificationService(Protocol):
    """Output port for sending notifications."""
    
    def send_email(self, to: str, subject: str, body: str) -> None: ...
    def send_sms(self, to: str, message: str) -> None: ...
```

### Use Cases with Injected Ports

```python
# domain/use_cases/create_order.py
from dataclasses import dataclass
from uuid import UUID

from my_app.domain.models.order import Order
from my_app.domain.ports.repository import Repository
from my_app.domain.ports.notification import NotificationService


@dataclass(frozen=True)
class CreateOrderInput:
    customer_id: UUID
    items: list[OrderItem]


@dataclass(frozen=True)
class CreateOrderOutput:
    order_id: UUID
    total: int


class CreateOrderUseCase:
    def __init__(
        self,
        order_repository: Repository[Order],
        customer_repository: Repository[Customer],
        notification_service: NotificationService,
    ) -> None:
        self._order_repository = order_repository
        self._customer_repository = customer_repository
        self._notification_service = notification_service

    def execute(self, input_data: CreateOrderInput) -> CreateOrderOutput:
        customer = self._customer_repository.find_by_id(input_data.customer_id)
        if not customer:
            raise CustomerNotFoundError(input_data.customer_id)
        
        order = Order.create(customer_id=customer.id, items=input_data.items)
        saved_order = self._order_repository.save(order)
        
        self._notification_service.send_email(
            to=customer.email,
            subject="Order Confirmation",
            body=f"Your order {saved_order.id} has been placed.",
        )
        
        return CreateOrderOutput(order_id=saved_order.id, total=saved_order.total)
```

### Adapters Implementing Ports

```python
# adapters/outbound/postgres_repository.py
from uuid import UUID

from my_app.domain.models.order import Order


class PostgresOrderRepository:
    """Adapter implementing Repository[Order] protocol."""
    
    def __init__(self, connection_string: str) -> None:
        self._connection_string = connection_string
        self._connection = self._create_connection()

    def save(self, entity: Order) -> Order:
        # PostgreSQL-specific implementation
        ...

    def find_by_id(self, entity_id: UUID) -> Order | None:
        # PostgreSQL-specific implementation
        ...

    def find_all(self) -> list[Order]:
        # PostgreSQL-specific implementation
        ...

    def delete(self, entity_id: UUID) -> bool:
        # PostgreSQL-specific implementation
        ...
```

## Testing with Dependency Injection

DI makes testing easy by allowing injection of fakes:

### Fakes for Testing

```python
# tests/fakes.py
from uuid import UUID

from my_app.domain.models.user import User


class FakeUserRepository:
    """Fake repository for unit testing."""
    
    def __init__(self) -> None:
        self._storage: dict[UUID, User] = {}

    def save(self, entity: User) -> User:
        self._storage[entity.id] = entity
        return entity

    def find_by_id(self, entity_id: UUID) -> User | None:
        return self._storage.get(entity_id)

    def find_all(self) -> list[User]:
        return list(self._storage.values())

    def delete(self, entity_id: UUID) -> bool:
        return self._storage.pop(entity_id, None) is not None


class FakeEmailer:
    """Fake emailer that records sent emails."""
    
    def __init__(self) -> None:
        self.sent_emails: list[dict] = []

    def send(self, to: str, subject: str, body: str) -> None:
        self.sent_emails.append({
            "to": to,
            "subject": subject,
            "body": body,
        })
```

### Unit Tests with Fakes

```python
# tests/domain/use_cases/test_create_user.py
import pytest

from my_app.domain.use_cases.create_user import CreateUserUseCase, CreateUserInput
from tests.fakes import FakeUserRepository, FakeEmailer


@pytest.fixture
def fake_repository() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def fake_emailer() -> FakeEmailer:
    return FakeEmailer()


@pytest.mark.unit
class TestCreateUserUseCase:
    def test_given_valid_input_when_execute_then_user_is_persisted(
        self,
        fake_repository: FakeUserRepository,
        fake_emailer: FakeEmailer,
    ) -> None:
        # Given
        use_case = CreateUserUseCase(
            repository=fake_repository,
            emailer=fake_emailer,
        )
        input_data = CreateUserInput(name="John", email="john@example.com")

        # When
        result = use_case.execute(input_data)

        # Then
        assert fake_repository.exists(result.id)

    def test_given_valid_input_when_execute_then_welcome_email_is_sent(
        self,
        fake_repository: FakeUserRepository,
        fake_emailer: FakeEmailer,
    ) -> None:
        # Given
        use_case = CreateUserUseCase(
            repository=fake_repository,
            emailer=fake_emailer,
        )
        input_data = CreateUserInput(name="John", email="john@example.com")

        # When
        use_case.execute(input_data)

        # Then
        assert len(fake_emailer.sent_emails) == 1
        assert fake_emailer.sent_emails[0]["to"] == "john@example.com"
```

## No Framework DI vs DI Containers

### Manual DI (Recommended)

For most Python projects, manual DI is sufficient and preferred:

- **Explicit**: Dependencies are visible in code
- **Simple**: No magic or configuration files
- **Debuggable**: Easy to trace dependency resolution
- **No learning curve**: No framework to learn

### When to Consider a DI Container

Only consider a DI container (like `dependency-injector`, `injector`, or `punq`) when:

- Very large application with hundreds of dependencies
- Complex dependency lifetimes (singleton, scoped, transient)
- Need for automatic dependency resolution
- Team is familiar with DI containers from other languages

```python
# Example with dependency-injector (only if needed)
from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    repository = providers.Singleton(
        PostgresUserRepository,
        connection_string=config.database_url,
    )
    
    emailer = providers.Singleton(
        SmtpEmailer,
        host=config.smtp_host,
        port=config.smtp_port,
    )
    
    create_user_use_case = providers.Factory(
        CreateUserUseCase,
        repository=repository,
        emailer=emailer,
    )
```

## Object Creation Summary

| What | Pattern | Where |
|------|---------|-------|
| Adapters, services | Factory functions | Composition root |
| Domain entities (new) | Factory methods (`@classmethod`) | Domain layer |
| Domain entities (from DB) | Constructor | Adapters |
| Domain entities (tests) | Constructor | Tests |

## Do

- Use constructor injection as the primary DI method
- Depend on Protocols (abstractions), not concrete implementations
- Create a single composition root at the application entry point
- Use **factory functions** for creating adapters (most Pythonic for infrastructure)
- Use **factory methods** only for domain entities that generate their own identity
- Keep the domain layer free of concrete adapter imports
- Use fakes for testing instead of mocks

## Don't

- Don't create dependencies inside classes (except for value objects)
- Don't use service locators or global registries
- Don't inject dependencies through setters (prefer constructor)
- Don't add a DI framework unless truly needed
- Don't let infrastructure concerns leak into domain through DI
- Don't make the composition root part of the domain layer
- Don't confuse factory functions (for adapters) with factory methods (for entities)
