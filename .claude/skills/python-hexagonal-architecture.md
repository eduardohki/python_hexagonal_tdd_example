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
│   ├── ports/              # Interfaces (abstract base classes)
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
3. **Ports are interfaces** - Defined as Protocols (preferred) in `domain/ports/`. Adapters satisfy these interfaces without inheritance.
4. **Keep the domain pure** - No framework dependencies in `domain/`.
5. **Use ports for external communication** - Never call external systems directly from use cases.
6. **Composition over inheritance** - Adapters satisfy protocols implicitly; no need to inherit from port interfaces.

## Code Templates

### Domain Entity

```python
from dataclasses import dataclass
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class ExampleEntity:
    """Domain entity with identity and business logic."""

    id: UUID
    name: str
    description: Optional[str] = None

    @classmethod
    def create(cls, name: str, description: Optional[str] = None) -> "ExampleEntity":
        """Factory method to create a new entity with a generated ID."""
        return cls(id=uuid4(), name=name, description=description)

    def update_name(self, new_name: str) -> "ExampleEntity":
        """Immutable update - returns new instance."""
        return ExampleEntity(id=self.id, name=new_name, description=self.description)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ExampleEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
```

### Port Interface (Protocol)

```python
from typing import Protocol, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class Repository(Protocol[T, ID]):
    """Repository protocol defining standard CRUD operations.
    
    Adapters satisfy this protocol by implementing these methods.
    No inheritance required — just implement the methods.
    """

    def save(self, entity: T) -> T: ...

    def find_by_id(self, entity_id: ID) -> T | None: ...

    def find_all(self) -> list[T]: ...

    def delete(self, entity_id: ID) -> bool: ...

    def exists(self, entity_id: ID) -> bool: ...
```

### Use Case

```python
from dataclasses import dataclass
from typing import Any

from <app_name>.domain.ports.repository import Repository


@dataclass
class CreateEntityInput:
    """Input DTO for the use case."""
    name: str
    description: str | None = None


@dataclass
class CreateEntityOutput:
    """Output DTO for the use case."""
    id: str
    name: str


class CreateEntityUseCase:
    """Use case with dependency injection through ports."""

    def __init__(self, repository: Repository[Any, Any]) -> None:
        self._repository = repository

    def execute(self, input_data: CreateEntityInput) -> CreateEntityOutput:
        """Execute the use case logic."""
        from <app_name>.domain.models.entity import Entity
        
        entity = Entity.create(name=input_data.name, description=input_data.description)
        saved = self._repository.save(entity)
        
        return CreateEntityOutput(id=str(saved.id), name=saved.name)
```

### Outbound Adapter

```python
from typing import Generic, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class InMemoryRepository(Generic[T, ID]):
    """In-memory adapter satisfying the Repository protocol.
    
    No inheritance from Repository needed — just implement the methods.
    This class implicitly satisfies Repository[T, ID] through structural typing.
    """

    def __init__(self) -> None:
        self._storage: dict[ID, T] = {}

    def save(self, entity: T) -> T:
        entity_id = self._get_entity_id(entity)
        self._storage[entity_id] = entity
        return entity

    def find_by_id(self, entity_id: ID) -> T | None:
        return self._storage.get(entity_id)

    def find_all(self) -> list[T]:
        return list(self._storage.values())

    def delete(self, entity_id: ID) -> bool:
        if entity_id in self._storage:
            del self._storage[entity_id]
            return True
        return False

    def exists(self, entity_id: ID) -> bool:
        return entity_id in self._storage

    def clear(self) -> None:
        """Clear all entities from storage. Useful for test cleanup."""
        self._storage.clear()

    def _get_entity_id(self, entity: T) -> ID:
        if hasattr(entity, "id"):
            return entity.id  # type: ignore
        raise ValueError(f"Entity {entity} does not have an 'id' attribute.")
```

## Common Tasks

### Adding a New Use Case

1. Create use case file: `src/<app_name>/domain/use_cases/<name>.py`
2. Define input/output DTOs as dataclasses
3. Inject required ports via constructor
4. Implement `execute()` method with business logic

### Adding a New Adapter

1. Create adapter file: `src/<app_name>/adapters/outbound/<name>.py` (or `inbound/`)
2. Implement the corresponding port interface
3. Handle infrastructure-specific concerns (DB connections, HTTP clients, etc.)

### Adding a New Port

1. Create interface: `src/<app_name>/domain/ports/<name>.py`
2. Define Protocol with method signatures (use `...` as body)
3. Use generics where appropriate for type safety
4. See `python-protocols-interfaces.md` for detailed patterns

## Do

- Add type hints to all functions
- Use dataclasses for domain models and DTOs
- Prefer immutability where possible
- Keep business logic in use cases and entities
- Use dependency injection for all external dependencies
- Use Protocols for port interfaces (not ABCs)
- Let adapters satisfy protocols implicitly (no inheritance)

## Don't

- Never import from `adapters/` inside `domain/`
- Never put framework dependencies in `domain/`
- Never call external systems directly from use cases
- Never let infrastructure concerns leak into the domain
- Don't use ABCs for ports when Protocols work (prefer structural typing)
- Don't force adapters to inherit from port interfaces
