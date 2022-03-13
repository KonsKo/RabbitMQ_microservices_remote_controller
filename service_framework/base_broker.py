"""Module for abstract broker implementation."""
from abc import ABC, abstractmethod
from typing import Any


class BaseBroker(ABC):
    """Abstract broker class."""

    @abstractmethod
    async def consume(self):
        """Create consume abstract method."""

    @abstractmethod
    async def publish(self, body: Any, destination: dict):
        """
        Create publish abstract method.

        Args:
            body (Any): message to publish
            destination (dict): address to publish
        """

    @abstractmethod
    async def stop(self):
        """Create stop abstract method."""
