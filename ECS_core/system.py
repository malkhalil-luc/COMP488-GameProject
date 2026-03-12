# System job is to execute a logic every frame.

# Every system like MovementSystem, CollisionSystem and RenderSystem will have methods called once
#at every frame like update()

# this base class will enforce these methods to be called all the time, otherwise an error will be raised. 
#ABC class: Abstract Base Class, python module used to define a base class, which is the template or contract 
# with other classes. |type safety and structure|
#EX: MovementSystem inherits from System but has no update(), TypeError raised, not a silent bug.

# ABC  uses @abstractmethod , a decorator from the same abc module to mark the method as required in any subclass


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
