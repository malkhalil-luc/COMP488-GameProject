

from abc import ABC, abstractmethod

class System(ABC):
    """
    Base class for all systems.
    """

    @abstractmethod
    def update(self, world, kwargs) -> None:
        """
        Runs once each frame.
        """
        pass
