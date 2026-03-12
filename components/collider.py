#what is the collision area
from dataclasses import dataclass
from ecs_core.component import Component


@ dataclass
class ColliderComponent (Component):
    """
    """
    width: int
    height: int