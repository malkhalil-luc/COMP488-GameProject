from dataclasses import dataclass

from ecs_core.component import Component


@dataclass
class LeaderMoveComponent(Component):
    target_x: float = 0.0
    target_y: float = 0.0
    timer: int = 0
