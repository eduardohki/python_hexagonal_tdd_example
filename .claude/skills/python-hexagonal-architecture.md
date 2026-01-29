# Python Hexagonal Architecture (Ports and Adapters)

This skill provides guidance for building Python applications using Hexagonal Architecture.

## Architecture Overview

```text
┌─────────────────┐   ┌──────────────────────────────────┐   ┌─────────────────┐
│                 │   │       Domain (The Hexagon)       │   │                 │
│ Inbound Adapters│   │ ┌────────┐ ┌──────┐ ┌─────────┐  │   │Outbound Adapters│
│                 │   │ │        │ │      │ │  Ports  │  │   │                 │
│ • REST API      │──▶│ │  Use   │─│Models│─│ (inter- │──│──▶│ • Repositories  │
│ • CLI           │   │ │ Cases  │ │      │ │ faces)  │  │   │ • External APIs │
│ • Message Queue │   │ └────────┘ └──────┘ └─────────┘  │   │ • Database      │
│                 │   │                                  │   │                 │
└─────────────────┘   └──────────────────────────────────┘   └─────────────────┘
   (adapters/                      (domain/)                     (adapters/
    inbound/)            models/ | use_cases/ | ports/             outbound/)
```

## Dependency Rule

Dependencies always point inward:
- Adapters depend on Ports
- Use Cases depend on Models and Ports
- Models have no external dependencies

**Critical**: Never import from `adapters/` inside `domain/`. The domain must remain pure with no framework or infrastructure dependencies.

## Project Structure

```
src/<app_name>/
├── domain/                 # The Hexagon (core business logic)
│   ├── models/             # Entities and value objects
│   ├── ports/              # Interfaces (Protocols) defined by use case needs
│   └── use_cases/          # Application-specific business rules
└── adapters/
    ├── inbound/            # Driving adapters (REST API, CLI, etc.)
    └── outbound/           # Driven adapters (repositories, external APIs)
```

## File Placement Rules

| Type | Location |
|------|----------|
| Entities / Value Objects | `src/<app_name>/domain/models/` |
| Port interfaces | `src/<app_name>/domain/ports/` |
| Use cases | `src/<app_name>/domain/use_cases/` |
| Inbound adapters | `src/<app_name>/adapters/inbound/` |
| Outbound adapters | `src/<app_name>/adapters/outbound/` |

## Key Principles

1. **Use cases belong inside the domain** - Not in a separate application layer. The domain folder represents the entire hexagon.
2. **Dependencies point inward** - Adapters depend on ports, never the reverse. Domain has no external dependencies.
3. **Ports are defined by use case needs** - Not generic CRUD interfaces. Each entity type has its own specific port with domain-meaningful methods.
4. **Ports are Protocols** - Defined as Protocols in `domain/ports/`. Adapters satisfy these interfaces without inheritance.
5. **Keep the domain pure** - No framework dependencies in `domain/`.
6. **Use ports for external communication** - Never call external systems directly from use cases.
7. **Composition over inheritance** - Adapters satisfy protocols implicitly; no need to inherit from port interfaces.

## Ports: Specific, Not Generic

**Wrong** — Generic CRUD repository:

```python
from typing import Protocol, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class Repository(Protocol[T, ID]):
    """Too generic — not driven by use case needs."""
    def save(self, entity: T) -> T: ...
    def find_by_id(self, entity_id: ID) -> T | None: ...
    def find_all(self) -> list[T]: ...
    def delete(self, entity_id: ID) -> bool: ...
```

**Right** — Specific port defined by use case needs:

```python
from typing import Protocol
from uuid import UUID

from my_app.domain.models.user import User


class UserRepository(Protocol):
    """Port defined by what the use cases actually need."""
    
    def save(self, user: User) -> User: ...
    def find_by_id(self, user_id: UUID) -> User | None: ...
    def find_by_email(self, email: str) -> User | None: ...
    def exists_with_email(self, email: str) -> bool: ...
```

Each entity gets its own repository port with domain-specific methods.

## Code Templates

### Domain Entity

```python
from dataclasses import dataclass
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class User:
    """Domain entity with identity and business logic."""

    id: UUID
    name: str
    email: str
    description: Optional[str] = None

    @classmethod
    def create(cls, name: str, email: str, description: Optional[str] = None) -> "User":
        """Factory method to create a new entity with a generated ID."""
        return cls(id=uuid4(), name=name, email=email, description=description)

    def update_email(self, new_email: str) -> "User":
        """Immutable update - returns new instance."""
        return User(id=self.id, name=self.name, email=new_email, description=self.description)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
```

### Port Interface (Protocol)

```python
from typing import Protocol
from uuid import UUID

from my_app.domain.models.user import User


class UserRepository(Protocol):
    """Repository protocol for User persistence.
    
    This port is defined by what the use cases need, not by
    generic data access patterns. Add methods here as use cases
    require them.

    Adapters satisfy this protocol by implementing these methods.
    No inheritance required — just implement the methods with matching signatures.
    """

    def save(self, user: User) -> User:
        """Persist a user."""
        ...

    def find_by_id(self, user_id: UUID) -> User | None:
        """Find a user by ID."""
        ...

    def find_by_email(self, email: str) -> User | None:
        """Find a user by email address."""
        ...

    def exists_with_email(self, email: str) -> bool:
        """Check if a user with this email already exists."""
        ...
```

### Use Case

```python
from dataclasses import dataclass
from uuid import UUID

from my_app.domain.models.user import User
from my_app.domain.ports.user_repository import UserRepository


@dataclass(frozen=True)
class CreateUserInput:
    """Input DTO for the use case."""
    name: str
    email: str
    description: str | None = None


@dataclass(frozen=True)
class CreateUserOutput:
    """Output DTO for the use case."""
    id: UUID
    name: str
    email: str


class CreateUserUseCase:
    """Use case with dependency injection through ports."""

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def execute(self, input_data: CreateUserInput) -> CreateUserOutput:
        """Execute the use case logic."""
        if self._repository.exists_with_email(input_data.email):
            raise ValueError(f"User with email {input_data.email} already exists")
        
        user = User.create(
            name=input_data.name,
            email=input_data.email,
            description=input_data.description,
        )
        saved = self._repository.save(user)
        
        return CreateUserOutput(id=saved.id, name=saved.name, email=saved.email)
```

### Outbound Adapter

```python
from uuid import UUID

from my_app.domain.models.user import User


class InMemoryUserRepository:
    """In-memory adapter satisfying the UserRepository protocol.
    
    No inheritance from UserRepository needed — just implement the methods.
    This class implicitly satisfies the protocol through structural typing.
    """

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

    def clear(self) -> None:
        """Adapter-specific method for testing. Not part of the protocol."""
        self._storage.clear()
```

## Common Tasks

### Adding a New Use Case

1. Identify what port methods the use case needs
2. Add methods to the entity's port (or create a new port)
3. Create use case file: `src/<app_name>/domain/use_cases/<name>.py`
4. Define input/output DTOs as dataclasses
5. Inject required ports via constructor
6. Implement `execute()` method with business logic

### Adding a New Adapter

1. Create adapter file: `src/<app_name>/adapters/outbound/<name>.py` (or `inbound/`)
2. Implement the methods defined in the port
3. No inheritance needed — just match the method signatures
4. Handle infrastructure-specific concerns (DB connections, HTTP clients, etc.)

### Adding a New Port

1. Create interface: `src/<app_name>/domain/ports/<entity>_repository.py`
2. Define Protocol with only the methods your use cases need
3. Use domain language in method names (`find_by_email`, not generic `find_by_field`)
4. See `python-protocols-interfaces.md` for detailed patterns

### Adding Methods to an Existing Port

1. Identify the use case that needs the new capability
2. Add the method to the port Protocol
3. Implement the method in all adapters that satisfy the port
4. Use the method in the use case

## Do

- Add type hints to all functions
- Use dataclasses for domain models and DTOs
- Prefer immutability where possible
- Keep business logic in use cases and entities
- Use dependency injection for all external dependencies
- Use Protocols for port interfaces (not ABCs)
- Let adapters satisfy protocols implicitly (no inheritance)
- Define ports by use case needs, not generic patterns
- Use domain language in port method names

## Don't

- Never import from `adapters/` inside `domain/`
- Never put framework dependencies in `domain/`
- Never call external systems directly from use cases
- Never let infrastructure concerns leak into the domain
- Don't use ABCs for ports when Protocols work (prefer structural typing)
- Don't force adapters to inherit from port interfaces
- Don't create generic `Repository[T, ID]` interfaces — be specific
- Don't add port methods "just in case" — add them when use cases need them
