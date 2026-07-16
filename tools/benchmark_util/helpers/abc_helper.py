"""
Provides implementation of abstract helper class, which all helpers should inherit from.
"""
from abc import ABC, abstractmethod

class Helper(ABC):
    """
    Abstract helper class. All helpers should inherit from this class and implement the run method.
    """
    @abstractmethod
    async def loop(self):
        """
        Main loop of the helper.
        """
        raise NotImplementedError("Loop method should be implemented by all helpers")


    @abstractmethod
    async def stop(self):
        """
        Stop the helper.
        """
        raise NotImplementedError("Stop method should be implemented by all helpers")
