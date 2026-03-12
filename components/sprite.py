#what does it look like

from dataclasses import dataclass, field
from typing import Tuple
from ecs_core.component import Component


@dataclass
class SpriteComponent(Component):
    """
    sprites is the 2d image that represent something in the game world, like player, enemy, fire, or anything drown on the screen
    width: int    - width in pixels
    height: int   - height in pixel
    color: Tuple[int,int,int] -  RGB color
    visible: bool - if false RenderSystem can skip the entity rendering
    """

    width: int
    height: int
    color: Tuple[int,int,int]
    visible: bool = field(default=True)
