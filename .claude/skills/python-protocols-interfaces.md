# Python Protocols and Interfaces

This skill provides guidance for defining interfaces in Python using Protocols, with a preference for composition over inheritance.

## Overview

Python offers two main approaches for defining interfaces:

1. **Protocols** (structural typing) - Preferred approach
2. **Abstract Base Classes (ABCs)** (nominal typing) - Use when necessary

**Prefer Protocols** because they support composition over inheritance and don't require classes to explicitly inherit from the interface.

## Protocols vs ABCs

### Protocols (Structural Typing)

With Protocols, a class implements an interface by simply having the right methods — no inheritance required:

```python
from typing import Protocol


class Repository(Protocol):
    """Interface defined as a Protocol."""

    def save(self, entity: Entity) -> Entity: ...
    def find_by_id(self, entity_id: UUID) -> Entity | None: ...


# No inheritance needed — just implement the methods
class InMemoryRepository:
    def save(self, entity: Entity) -> Entity:
        # implementation
        ...

    def find_by_id(self, entity_id: UUID) -> Entity | None:
        # implementation
        ...


# This works because InMemoryRepository has the right structure
def process(repo: Repository) -> None:
    repo.save(...)
```

### Abstract Base Classes (Nominal Typing)

With ABCs, a class must explicitly inherit from the interface:

```python
from abc import ABC, abstractmethod


class Repository(ABC):
    """Interface defined as an ABC."""

    @abstractmethod
    def save(self, entity: Entity) -> Entity:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, entity_id: UUID) -> Entity | None:
        raise NotImplementedError


# Must inherit from Repository
class InMemoryRepository(Repository):
    def save(self, entity: Entity) -> Entity:
        # implementation
        ...

    def find_by_id(self, entity_id: UUID) -> Entity | None:
        # implementation
        ...
```

## When to Use Protocols (Preferred)

Use Protocols when:

- **Defining ports in hexagonal architecture** — Adapters don't need to know about domain interfaces
- **Working with external libraries** — You can't modify their classes to inherit from your ABCs
- **Preferring composition** — No inheritance hierarchy required
- **Duck typing with type safety** — "If it walks like a duck..."
- **Multiple interface implementation** — A class can satisfy multiple protocols naturally

```python
from typing import Protocol
from uuid import UUID


class Readable(Protocol):
    def read(self, id: UUID) -> Entity | None: ...


class Writable(Protocol):
    def write(self, entity: Entity) -> Entity: ...


class Deletable(Protocol):
    def delete(self, id: UUID) -> bool: ...


# Satisfies all three protocols without multiple inheritance
class FullRepository:
    def read(self, id: UUID) -> Entity | None:
        ...

    def write(self, entity: Entity) -> Entity:
        ...

    def delete(self, id: UUID) -> bool:
        ...


# Function only needs Readable
def get_entity(repo: Readable, id: UUID) -> Entity | None:
    return repo.read(id)


# Function needs both Readable and Writable
def copy_entity(source: Readable, dest: Writable, id: UUID) -> Entity | None:
    entity = source.read(id)
    if entity:
        return dest.write(entity)
    return None
```

## When to Use ABCs

Use ABCs when:

- **You need to enforce inheritance** — Runtime checks with `isinstance()`
- **You want to provide default implementations** — Mix of abstract and concrete methods
- **Registration is needed** — Using `register()` for virtual subclasses
- **Framework requirements** — Some frameworks expect ABC-based interfaces

```python
from abc import ABC, abstractmethod


class EventHandler(ABC):
    """ABC with default implementation."""

    @abstractmethod
    def handle(self, event: Event) -> None:
        """Must be implemented by subclasses."""
        raise NotImplementedError

    def can_handle(self, event: Event) -> bool:
        """Default implementation — can be overridden."""
        return True

    def on_error(self, event: Event, error: Exception) -> None:
        """Default error handling — can be overridden."""
        print(f"Error handling {event}: {error}")
```

## Protocol Patterns

### Basic Protocol

```python
from typing import Protocol


class Logger(Protocol):
    def log(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...
```

### Protocol with Properties

```python
from typing import Protocol


class HasId(Protocol):
    @property
    def id(self) -> UUID: ...


class HasTimestamp(Protocol):
    @property
    def created_at(self) -> datetime: ...
    @property
    def updated_at(self) -> datetime: ...
```

### Generic Protocols

```python
from typing import Protocol, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class Repository(Protocol[T, ID]):
    def save(self, entity: T) -> T: ...
    def find_by_id(self, entity_id: ID) -> T | None: ...
    def find_all(self) -> list[T]: ...
    def delete(self, entity_id: ID) -> bool: ...
```

### Callable Protocol

```python
from typing import Protocol


class Handler(Protocol):
    def __call__(self, request: Request) -> Response: ...


# Any callable with this signature satisfies Handler
def my_handler(request: Request) -> Response:
    return Response(...)


# Class instances too
class MyHandler:
    def __call__(self, request: Request) -> Response:
        return Response(...)
```

### Protocol Inheritance (Composition of Interfaces)

```python
from typing import Protocol


class Readable(Protocol):
    def read(self, id: UUID) -> Entity | None: ...


class Writable(Protocol):
    def write(self, entity: Entity) -> Entity: ...


class ReadWriteRepository(Readable, Writable, Protocol):
    """Combines Readable and Writable protocols."""
    ...
```

## Runtime Checking with Protocols

By default, Protocols are for static type checking only. For runtime checks, use `runtime_checkable`:

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...


# Now you can use isinstance()
def safe_close(obj: object) -> None:
    if isinstance(obj, Closeable):
        obj.close()
```

**Note**: Runtime checking only verifies method existence, not signatures. Use sparingly.

## Hexagonal Architecture with Protocols

### Defining Ports as Protocols

```python
# domain/ports/repository.py
from typing import Protocol, TypeVar
from uuid import UUID

T = TypeVar("T")


class Repository(Protocol[T]):
    """Output port for data persistence."""

    def save(self, entity: T) -> T: ...
    def find_by_id(self, entity_id: UUID) -> T | None: ...
    def find_all(self) -> list[T]: ...
    def delete(self, entity_id: UUID) -> bool: ...
    def exists(self, entity_id: UUID) -> bool: ...
```

```python
# domain/ports/event_publisher.py
from typing import Protocol

from my_app.domain.models.event import DomainEvent


class EventPublisher(Protocol):
    """Output port for publishing domain events."""

    def publish(self, event: DomainEvent) -> None: ...
    def publish_all(self, events: list[DomainEvent]) -> None: ...
```

### Implementing Ports (Adapters)

```python
# adapters/outbound/in_memory_repository.py
from uuid import UUID

from my_app.domain.models.user import User


# No inheritance from Repository Protocol needed!
class InMemoryUserRepository:
    """Adapter implementing Repository protocol."""

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
        if entity_id in self._storage:
            del self._storage[entity_id]
            return True
        return False

    def exists(self, entity_id: UUID) -> bool:
        return entity_id in self._storage
```

### Use Cases with Protocol Dependencies

```python
# domain/use_cases/create_user.py
from dataclasses import dataclass
from uuid import UUID

from my_app.domain.models.user import User
from my_app.domain.ports.repository import Repository
from my_app.domain.ports.event_publisher import EventPublisher


@dataclass(frozen=True)
class CreateUserInput:
    name: str
    email: str


@dataclass(frozen=True)
class CreateUserOutput:
    id: UUID
    name: str


class CreateUserUseCase:
    def __init__(
        self,
        repository: Repository[User],
        event_publisher: EventPublisher,
    ) -> None:
        self._repository = repository
        self._event_publisher = event_publisher

    def execute(self, input_data: CreateUserInput) -> CreateUserOutput:
        user = User.create(name=input_data.name, email=input_data.email)
        saved_user = self._repository.save(user)
        self._event_publisher.publish(UserCreatedEvent(user_id=saved_user.id))
        return CreateUserOutput(id=saved_user.id, name=saved_user.name)
```

## Testing with Protocols

Fakes naturally satisfy protocols without inheritance:

```python
# tests/fakes.py
from uuid import UUID

from my_app.domain.models.user import User


class FakeUserRepository:
    """Fake for testing — satisfies Repository[User] protocol."""

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

    def exists(self, entity_id: UUID) -> bool:
        return entity_id in self._storage


class FakeEventPublisher:
    """Fake for testing — satisfies EventPublisher protocol."""

    def __init__(self) -> None:
        self.published_events: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        self.published_events.append(event)

    def publish_all(self, events: list[DomainEvent]) -> None:
        self.published_events.extend(events)
```

## Composition Over Inheritance

### Instead of Deep Hierarchies

```python
# Avoid this inheritance hierarchy
class BaseRepository(ABC):
    ...

class CachingRepository(BaseRepository):
    ...

class LoggingCachingRepository(CachingRepository):
    ...
```

### Use Composition with Protocols

```python
from typing import Protocol


class Repository(Protocol[T]):
    def save(self, entity: T) -> T: ...
    def find_by_id(self, entity_id: UUID) -> T | None: ...


class Cache(Protocol[T]):
    def get(self, key: str) -> T | None: ...
    def set(self, key: str, value: T) -> None: ...


class Logger(Protocol):
    def log(self, message: str) -> None: ...


# Compose behaviors
class CachingRepository:
    def __init__(self, inner: Repository[T], cache: Cache[T]) -> None:
        self._inner = inner
        self._cache = cache

    def save(self, entity: T) -> T:
        result = self._inner.save(entity)
        self._cache.set(str(entity.id), result)
        return result

    def find_by_id(self, entity_id: UUID) -> T | None:
        cached = self._cache.get(str(entity_id))
        if cached:
            return cached
        return self._inner.find_by_id(entity_id)


class LoggingRepository:
    def __init__(self, inner: Repository[T], logger: Logger) -> None:
        self._inner = inner
        self._logger = logger

    def save(self, entity: T) -> T:
        self._logger.log(f"Saving entity {entity}")
        result = self._inner.save(entity)
        self._logger.log(f"Saved entity {result}")
        return result

    def find_by_id(self, entity_id: UUID) -> T | None:
        self._logger.log(f"Finding entity {entity_id}")
        return self._inner.find_by_id(entity_id)
```

## Do

- Prefer Protocols over ABCs for defining interfaces
- Use composition to combine behaviors
- Keep protocols small and focused (Interface Segregation)
- Use generic protocols for reusable interfaces
- Let classes satisfy protocols implicitly (no inheritance)
- Use `@runtime_checkable` sparingly and only when needed

## Don't

- Don't create deep inheritance hierarchies
- Don't use ABCs just because other languages do
- Don't add implementation details to protocols
- Don't use `isinstance()` checks with non-runtime-checkable protocols
- Don't force classes to inherit from protocols unnecessarily
- Don't mix protocol definitions with concrete implementations
