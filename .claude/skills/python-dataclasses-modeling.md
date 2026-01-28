# Python Dataclasses and Domain Modeling

This skill provides guidance for using dataclasses to model domain entities and value objects in Python applications.

## Object Creation Patterns

Python offers three patterns for creating objects. Use the right one for each context:

| Pattern | When to Use | Location |
|---------|-------------|----------|
| **Constructor** (`__init__`) | Caller provides all values, including ID | Tests, reconstituting from persistence, adapters |
| **Factory method** (`@classmethod`) | Entity generates its own identity/timestamps | Domain layer, entity creation |
| **Factory function** | Creating adapters, wiring dependencies, config-based creation | Composition root, infrastructure |

### Constructor (Direct Instantiation)

Use when the caller already has all the data, including the ID:

```python
# In tests - you control the ID for assertions
user = User(id=UUID("12345678-1234-5678-1234-567812345678"), name="John", email="john@example.com")

# In adapters - reconstituting from database
user = User(id=row["id"], name=row["name"], email=row["email"])
```

### Factory Method (`@classmethod`)

Use when the entity should generate its own identity or derived values:

```python
# In domain/use cases - entity controls its creation
user = User.create(name="John", email="john@example.com")  # ID generated internally
```

### Factory Function

Use for infrastructure concerns, especially in the composition root:

```python
# In composition root - config-based creation
def create_repository(config: Config) -> Repository[User]:
    if config.use_in_memory:
        return InMemoryRepository()
    return PostgresRepository(config.database_url)
```

### Why This Matters

- **Constructors are Pythonic** for simple, explicit creation
- **Factory methods** keep identity generation with the entity (domain logic stays in domain)
- **Factory functions** keep infrastructure decisions out of domain classes

## Overview

Dataclasses provide a declarative way to define classes that primarily hold data. They automatically generate `__init__`, `__repr__`, `__eq__`, and other methods, reducing boilerplate while keeping code explicit and type-safe.

## Basic Dataclass

```python
from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    email: str
```

This automatically generates:
- `__init__(self, id: int, name: str, email: str)`
- `__repr__(self)` for debugging
- `__eq__(self, other)` for equality comparison

## Domain Modeling Concepts

### Entities vs Value Objects

**Entities** have identity — two entities with the same attributes but different IDs are different:

```python
from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass
class User:
    """Entity: identified by its unique ID."""
    id: UUID
    name: str
    email: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
```

**Value Objects** have no identity — two value objects with the same attributes are equal:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    """Value Object: identified by its attributes."""
    amount: int
    currency: str
```

## Immutability

### Frozen Dataclasses

Use `frozen=True` for immutable objects (recommended for value objects):

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    street: str
    city: str
    postal_code: str
```

Frozen dataclasses:
- Cannot be modified after creation
- Are automatically hashable
- Are thread-safe

### Immutable Updates

For entities that need updates, return new instances instead of mutating:

```python
from dataclasses import dataclass
from uuid import UUID


@dataclass
class Product:
    id: UUID
    name: str
    price: int

    def with_price(self, new_price: int) -> "Product":
        """Return a new Product with updated price."""
        return Product(
            id=self.id,
            name=self.name,
            price=new_price,
        )

    def with_name(self, new_name: str) -> "Product":
        """Return a new Product with updated name."""
        return Product(
            id=self.id,
            name=new_name,
            price=self.price,
        )
```

### Using `dataclasses.replace()`

For simpler immutable updates:

```python
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Config:
    debug: bool
    log_level: str
    timeout: int


config = Config(debug=False, log_level="INFO", timeout=30)
new_config = replace(config, debug=True)
```

## Factory Methods

Use factory methods (`@classmethod`) when the entity should control its own creation, particularly for generating identity or setting initial state:

```python
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Order:
    id: UUID
    customer_id: UUID
    created_at: datetime
    status: str
    total: int

    @classmethod
    def create(cls, customer_id: UUID, total: int) -> "Order":
        """
        Factory method for creating NEW orders.
        
        Use this in use cases when creating a new order.
        The entity controls its own identity generation.
        """
        return cls(
            id=uuid4(),
            customer_id=customer_id,
            created_at=datetime.now(),
            status="pending",
            total=total,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Order":
        """
        Factory method for reconstituting from external data.
        
        Use this in adapters when loading from database/API responses.
        All values come from the external source.
        """
        return cls(
            id=UUID(data["id"]),
            customer_id=UUID(data["customer_id"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            status=data["status"],
            total=data["total"],
        )


# Usage in use case (domain layer):
order = Order.create(customer_id=customer.id, total=1000)

# Usage in adapter (infrastructure layer):
order = Order.from_dict(database_row)

# Usage in tests (explicit control):
order = Order(
    id=UUID("12345678-1234-5678-1234-567812345678"),
    customer_id=UUID("87654321-4321-8765-4321-876543218765"),
    created_at=datetime(2024, 1, 1, 12, 0, 0),
    status="pending",
    total=1000,
)
```

## Default Values and Fields

### Simple Defaults

```python
from dataclasses import dataclass


@dataclass
class Settings:
    name: str
    debug: bool = False
    max_retries: int = 3
```

### Mutable Default Values

Never use mutable defaults directly. Use `field()` with `default_factory`:

```python
from dataclasses import dataclass, field


# WRONG - shared mutable default
@dataclass
class BadExample:
    items: list[str] = []  # Bug! All instances share this list


# CORRECT - factory creates new list per instance
@dataclass
class GoodExample:
    items: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
```

### Computed Fields

Use `field(init=False)` for fields not set in `__init__`:

```python
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Event:
    name: str
    created_at: datetime = field(init=False)

    def __post_init__(self) -> None:
        self.created_at = datetime.now()
```

### Excluded Fields

Use `field(repr=False, compare=False)` to exclude from generated methods:

```python
from dataclasses import dataclass, field


@dataclass
class User:
    id: int
    name: str
    password_hash: str = field(repr=False, compare=False)
```

## Post-Init Processing

Use `__post_init__` for validation or derived values:

```python
from dataclasses import dataclass


@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Dimensions must be positive")
        self.area = self.width * self.height
```

## Input/Output DTOs

Use dataclasses for use case inputs and outputs:

```python
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateUserInput:
    """Input DTO for user creation."""
    name: str
    email: str


@dataclass(frozen=True)
class CreateUserOutput:
    """Output DTO for user creation."""
    id: UUID
    name: str
    email: str


@dataclass(frozen=True)
class UserNotFoundError:
    """Error DTO when user is not found."""
    user_id: UUID
    message: str = "User not found"
```

## Inheritance

Dataclasses support inheritance, but be careful with field ordering:

```python
from dataclasses import dataclass
from uuid import UUID


@dataclass
class BaseEntity:
    id: UUID


@dataclass
class User(BaseEntity):
    name: str
    email: str
```

**Note**: Parent fields without defaults must come before child fields with defaults.

## Slots for Performance

Use `slots=True` for memory efficiency (Python 3.10+):

```python
from dataclasses import dataclass


@dataclass(slots=True)
class Point:
    x: float
    y: float
```

Slots:
- Reduce memory usage
- Faster attribute access
- Prevent dynamic attribute creation

## Comparison and Ordering

Enable ordering with `order=True`:

```python
from dataclasses import dataclass


@dataclass(order=True, frozen=True)
class Version:
    major: int
    minor: int
    patch: int


v1 = Version(1, 0, 0)
v2 = Version(2, 0, 0)
assert v1 < v2
```

## Pattern: Rich Domain Models

Combine dataclasses with business logic methods:

```python
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass
class BankAccount:
    id: UUID
    owner: str
    balance: Decimal

    @classmethod
    def create(cls, owner: str, initial_deposit: Decimal = Decimal("0")) -> "BankAccount":
        if initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative")
        return cls(id=uuid4(), owner=owner, balance=initial_deposit)

    def deposit(self, amount: Decimal) -> "BankAccount":
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        return BankAccount(
            id=self.id,
            owner=self.owner,
            balance=self.balance + amount,
        )

    def withdraw(self, amount: Decimal) -> "BankAccount":
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        return BankAccount(
            id=self.id,
            owner=self.owner,
            balance=self.balance - amount,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BankAccount):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
```

## Do

- Use `frozen=True` for value objects
- Use **constructors** for tests and when reconstituting from persistence
- Use **factory methods** (`@classmethod`) when entity generates its own identity
- Use **factory functions** in composition root for config-based adapter creation
- Use `field(default_factory=...)` for mutable defaults
- Use `__post_init__` for validation
- Prefer immutable updates (return new instances)
- Add type hints to all fields
- Override `__eq__` and `__hash__` for entities based on ID

## Don't

- Don't use factory methods just to avoid passing an ID in tests
- Don't use factory functions inside domain classes
- Don't generate IDs in adapters (let the entity or caller control this)
- Don't use mutable default values directly
- Don't mutate frozen dataclasses (use `replace()`)
- Don't put infrastructure concerns in domain models
- Don't skip validation in factory methods
- Don't inherit from multiple dataclasses with overlapping fields
- Don't use dataclasses for classes with complex behavior and little data
