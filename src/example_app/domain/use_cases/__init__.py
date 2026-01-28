"""
Use cases - Application-specific business rules.

Use cases orchestrate the flow of data between domain entities and ports.
They represent the actions that users can perform with the system.

In hexagonal architecture, use cases:
- Define the inbound ports (the API of the domain)
- Coordinate domain objects to fulfill business operations
- Depend on outbound ports for external communication (e.g., persistence)
"""
