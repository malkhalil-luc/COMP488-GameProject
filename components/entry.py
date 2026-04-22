from dataclasses import dataclass

from ecs_core.component import Component


@dataclass
class EntryComponent(Component):
    active: bool = True
    speed: float = 2.8
    delay: int = 0
