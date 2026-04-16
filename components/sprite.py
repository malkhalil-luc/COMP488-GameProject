from dataclasses import dataclass, field
from typing import Tuple
from ecs_core.component import Component


@dataclass
class SpriteComponent(Component):
    """
    Stores the size, color, and visibility of something we draw.
    """

    width: int
    height: int
    color: Tuple[int,int,int]
    visible: bool = field(default=True)
