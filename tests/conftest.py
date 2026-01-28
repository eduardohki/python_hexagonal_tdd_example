"""
Pytest configuration and shared fixtures.

This module contains fixtures that are shared across all test modules.
Fixtures defined here are automatically available to all tests.
"""

import pytest


@pytest.fixture
def app_config() -> dict:
    """Provide test application configuration."""
    return {
        "environment": "test",
        "debug": True,
    }
