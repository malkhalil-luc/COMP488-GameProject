from dataclasses import dataclass
from ecs_core.component import Component

@dataclass
class PositionComponent(Component):
    """
    Stores where an entity is on the screen.
    """

    x: float
    y: float
