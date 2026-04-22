from __future__ import annotations

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
    image_path: str | None = None
    visible: bool = field(default=True)
