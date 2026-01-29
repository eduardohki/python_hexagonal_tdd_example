# Python Protocols and Interfaces

This skill provides guidance for defining interfaces in Python using Protocols, with a preference for composition over inheritance.

## Overview

Python offers two main approaches for defining interfaces:

1. **Protocols** (structural typing) - Preferred approach
2. **Abstract Base Classes (ABCs)** (nominal typing) - Use when necessary

**Prefer Protocols** because they support composition over inheritance and don't require classes to explicitly inherit from the interface.

## Specific Ports, Not Generic Interfaces

In hexagonal architecture, ports should be **defined by use case needs**, not as generic CRUD interfaces.

**Avoid** generic repositories with type parameters:

```python
# Too generic — not driven by use case needs
class Repository(Protocol[T, ID]):
    def save(self, entity: T) -> T: ...
    def find_by_id(self, entity_id: ID) -> T | None: ...
```

**Prefer** specific ports with domain-meaningful methods:

```python
# Specific to User, with methods the use cases actually need
class UserRepository(Protocol):
    def save(self, user: User) -> User: ...
    def find_by_id(self, user_id: UUID) -> User | None: ...
    def find_by_email(self, email: str) -> User | None: ...
    def exists_with_email(self, email: str) -> bool: ...
```

Benefits:
- No complex generics or type variance issues
- Methods use domain language (`find_by_email` vs `find_by_field`)
- Each port only has methods that use cases need
- Simpler to implement and test

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

### Generic Protocols (Use Sparingly)

Generic protocols add complexity. Prefer specific protocols for domain ports.

```python
from typing import Protocol, TypeVar

T = TypeVar("T")


class Serializer(Protocol[T]):
    """Generic protocol — appropriate for cross-cutting utilities, not domain ports."""
    def serialize(self, obj: T) -> bytes: ...
    def deserialize(self, data: bytes) -> T: ...
```

**For domain ports, prefer specific protocols without generics:**

```python
class OrderRepository(Protocol):
    """Specific protocol — defined by use case needs."""
    def save(self, order: Order) -> Order: ...
    def find_by_id(self, order_id: UUID) -> Order | None: ...
    def find_pending_for_customer(self, customer_id: UUID) -> list[Order]: ...
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

Ports are defined by **what the use case needs**, not generic patterns:

```python
# domain/ports/user_repository.py
from typing import Protocol
from uuid import UUID

from my_app.domain.models.user import User


class UserRepository(Protocol):
    """Output port for User persistence — defined by use case needs."""

    def save(self, user: User) -> User: ...
    def find_by_id(self, user_id: UUID) -> User | None: ...
    def find_by_email(self, email: str) -> User | None: ...
    def exists_with_email(self, email: str) -> bool: ...
```

```python
# domain/ports/order_repository.py
from typing import Protocol
from uuid import UUID

from my_app.domain.models.order import Order


class OrderRepository(Protocol):
    """Output port for Order persistence — defined by use case needs."""

    def save(self, order: Order) -> Order: ...
    def find_by_id(self, order_id: UUID) -> Order | None: ...
    def find_pending_for_customer(self, customer_id: UUID) -> list[Order]: ...
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
# adapters/outbound/in_memory_user_repository.py
from uuid import UUID

from my_app.domain.models.user import User


# No inheritance from UserRepository Protocol needed!
class InMemoryUserRepository:
    """Adapter satisfying UserRepository protocol."""

    def __init__(self) -> None:
        self._storage: dict[UUID, User] = {}

    def save(self, user: User) -> User:
        self._storage[user.id] = user
        return user

    def find_by_id(self, user_id: UUID) -> User | None:
        return self._storage.get(user_id)

    def find_by_email(self, email: str) -> User | None:
        for user in self._storage.values():
            if user.email == email:
                return user
        return None

    def exists_with_email(self, email: str) -> bool:
        return self.find_by_email(email) is not None
```

### Use Cases with Protocol Dependencies

```python
# domain/use_cases/create_user.py
from dataclasses import dataclass
from uuid import UUID

from my_app.domain.models.user import User
from my_app.domain.ports.user_repository import UserRepository
from my_app.domain.ports.event_publisher import EventPublisher


@dataclass(frozen=True)
class CreateUserInput:
    name: str
    email: str


@dataclass(frozen=True)
class CreateUserOutput:
    id: UUID
    name: str
    email: str


class CreateUserUseCase:
    def __init__(
        self,
        repository: UserRepository,
        event_publisher: EventPublisher,
    ) -> None:
        self._repository = repository
        self._event_publisher = event_publisher

    def execute(self, input_data: CreateUserInput) -> CreateUserOutput:
        # Use domain-specific method from the port
        if self._repository.exists_with_email(input_data.email):
            raise ValueError(f"User with email {input_data.email} already exists")
        
        user = User.create(name=input_data.name, email=input_data.email)
        saved_user = self._repository.save(user)
        self._event_publisher.publish(UserCreatedEvent(user_id=saved_user.id))
        
        return CreateUserOutput(id=saved_user.id, name=saved_user.name, email=saved_user.email)
```

## Testing with Protocols

Fakes naturally satisfy protocols without inheritance:

```python
# tests/fakes.py
from uuid import UUID

from my_app.domain.models.user import User


class FakeUserRepository:
    """Fake for testing — satisfies UserRepository protocol."""

    def __init__(self) -> None:
        self._storage: dict[UUID, User] = {}

    def save(self, user: User) -> User:
        self._storage[user.id] = user
        return user

    def find_by_id(self, user_id: UUID) -> User | None:
        return self._storage.get(user_id)

    def find_by_email(self, email: str) -> User | None:
        for user in self._storage.values():
            if user.email == email:
                return user
        return None

    def exists_with_email(self, email: str) -> bool:
        return self.find_by_email(email) is not None


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
- Define ports by use case needs, not generic patterns
- Use domain language in port method names (`find_by_email`, not `find_by_field`)
- Let classes satisfy protocols implicitly (no inheritance)
- Use `@runtime_checkable` sparingly and only when needed

## Don't

- Don't create deep inheritance hierarchies
- Don't use ABCs just because other languages do
- Don't add implementation details to protocols
- Don't use `isinstance()` checks with non-runtime-checkable protocols
- Don't force classes to inherit from protocols unnecessarily
- Don't mix protocol definitions with concrete implementations
- Don't create generic `Repository[T, ID]` protocols — be specific to each entity
- Don't add port methods "just in case" — add them when use cases need them
