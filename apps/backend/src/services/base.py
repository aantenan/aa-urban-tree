"""Base service pattern: constructor dependency injection for testability."""
from typing import Any


class BaseService:
    """
    Optional base for feature services. Dependencies are injected via constructor
    so tests can pass mocks. Service methods are pure: input params, return results.
    """

    def __init__(self, **deps: Any) -> None:
        for key, value in deps.items():
            setattr(self, key, value)
