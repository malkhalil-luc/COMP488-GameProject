#how much HP does it have
from dataclasses import dataclass
from ECS_core.component import Component


@dataclass
class HealthComponent(Component):

    """
    current and maximum health of an entity
    hp: int current health, updated y the Damage System
    max_hp: starting health and is the reference for HP bar
    """

    hp: int
    max_hp: int