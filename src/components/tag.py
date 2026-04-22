from dataclasses import dataclass
from ecs_core.component import Component


@dataclass
class TagComponent(Component):
    """
    Stores a simple label like player, enemy, or bullet.
    """
    label: str
