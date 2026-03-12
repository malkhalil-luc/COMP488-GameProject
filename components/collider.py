#what is the collistion area
from dataclasses import dataclass
from ecs_core.component import Component


@ dataclass
class ColliderSprite (Component):
    """
    """
    width: int
    height: int