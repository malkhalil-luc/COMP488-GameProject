from dataclasses import dataclass, field
from ecs_core.component import Component


@dataclass
class VelocityComponent(Component):
    """
    Stores how fast an entity moves on the x and y axes.
    """

    vx: float = field(default=0.0)
    vy: float = field(default=0.0)
