from dataclasses import dataclass
from ecs_core.component import Component


@dataclass
class ColliderComponent(Component):
    """
    Stores the hitbox size used for collisions.
    """
    width: int
    height: int
