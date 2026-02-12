"""Service registry for lifecycle and discovery of services beyond the core container."""
from typing import Any, Callable

_registry: dict[str, Callable[[], Any]] = {}


def register(name: str, factory: Callable[[], Any]) -> None:
    """Register a service factory. Overwrites existing registration for name."""
    _registry[name] = factory


def get(name: str) -> Any:
    """Resolve a service by name. Raises KeyError if not registered."""
    if name not in _registry:
        raise KeyError(f"Service not registered: {name}")
    return _registry[name]()


def clear() -> None:
    """Clear all registrations (e.g. for tests)."""
    _registry.clear()
