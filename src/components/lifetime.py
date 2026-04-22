from __future__ import annotations

from dataclasses import dataclass, field
from ecs_core.component import Component

@dataclass
class LifetimeComponent(Component):
    """
    Stores when an entity should be removed automatically.
    """
    destroy_when_offscreen: bool = field(default=True)
    frames_left: int | None = field(default=None)
