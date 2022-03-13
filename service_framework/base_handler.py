"""
Abstract class for handler.

Init method with args and kwargs crated for purpose to point out that if
someone wants to add custom parameters to constructor.
This parameters need to pass to async_service.launch_service function.

"""
from abc import ABC, abstractmethod
from typing import Callable, Optional


class BaseHandler(ABC):
    """Abstract handler class."""

    @abstractmethod
    def __init__(self, *args, **kwargs):
        """
        Abstract init method.

        Args:
            args: extra arguments
            kwargs: extra key arguments

        """

    @abstractmethod
    def prepare_handler(self, publisher: Callable, config: Optional[dict]):
        """
        Create prepare abstract method.

        Args:
            publisher (Callable): async broker publish method
            config (Optional[dict]): PowerShell config

        """

    @abstractmethod
    async def call_handler(self, body: Optional[bytes]):
        """
        Create call abstract method.

        Args:
            body (Optional[bytes]): data from broker to work with

        """

    @abstractmethod
    async def stop_handler(self):
        """Create stop abstract method."""
