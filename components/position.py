from dataclasses import dataclass
from ecs_core.component import Component

@dataclass
class PositionComponent (Component):
    """
    Position on scree.
    Used by different systems.

    Type float: 
            - for movement is is multiplied by dt which is float. so the result is float
            - for pygame.draw.rect() will cast it to int when it draws

    """

    x: float
    y: float