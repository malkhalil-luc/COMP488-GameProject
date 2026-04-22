from dataclasses import dataclass

from ecs_core.component import Component


@dataclass
class FormationComponent(Component):
    base_x: float
    base_y: float
    col_index: int
