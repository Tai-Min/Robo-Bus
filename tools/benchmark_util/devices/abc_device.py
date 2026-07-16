"""
Provides interface for physical devices.
All devices should inherit from this class and implement the run method.
"""
from abc import ABC, abstractmethod
import logging


logger = logging.getLogger(__name__)


class Device(ABC):
    """
    Abstract device class. All devices should inherit from this class and implement the run method.
    """
    def __init__(self, name: str, priority: int = 999):
        """
        Constructor.

        @param name: Name of the device.
        @param priority: Priority of the device. Devices with lower priority will be started first.
        """
        logger.debug("%s: Init, priority=%d", name, priority)
        self._name = name
        self.__priority = priority


    def get_name(self) -> str:
        """
        Get name of the device.

        @return Name string.
        """
        return self._name


    def get_priority(self) -> int:
        """
        Get the priority of the device.

        @return Priority of the device.
        """
        return self.__priority


    @abstractmethod
    async def open(self) -> bool:
        """
        Open the device.

        @return True on success, false otherwise.
        """
        raise NotImplementedError("Open method should be implemented by all devices")


    @abstractmethod
    async def loop(self):
        """
        Main loop of the device.
        """
        raise NotImplementedError("Loop method should be implemented by all devices")
