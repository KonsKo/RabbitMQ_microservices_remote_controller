"""Module for abstract main_service implementation."""
from abc import ABC, abstractmethod


class BaseService(ABC):
    """Abstract main_service class."""

    @abstractmethod
    def prepare_to_run(self):
        """Create prepare abstract method."""

    @abstractmethod
    def service_run(self):
        """Create run abstract method."""
