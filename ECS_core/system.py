

from abc import ABC, abstractmethod

class System(ABC):
    """
    Base class of all systems,
    enforce all systems to implement it's methods
    """

    @abstractmethod
    def update (self, world,kwargs) -> None:
        """
        Called once at every frame

        Parameters:
            - world: ECS registry, query entities and components here
            - **kwargs: frame data, like game state, dt. Each system unpack what data it needs
        """
        pass
