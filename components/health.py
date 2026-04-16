from dataclasses import dataclass
from ecs_core.component import Component


@dataclass
class HealthComponent(Component):
    """
    Stores current health and max health.
    """

    hp: int
    max_hp: int
