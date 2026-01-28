"""
Domain layer - The core of the hexagonal architecture.

This layer contains:
- models: Domain entities and value objects
- ports: Interfaces (abstract base classes) that define how the domain
         interacts with the outside world
- use_cases: Application-specific business rules that orchestrate
             domain objects and coordinate with adapters through ports
"""
