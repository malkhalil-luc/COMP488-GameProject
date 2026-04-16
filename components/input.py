from dataclasses import dataclass
from ecs_core.component import Component


@dataclass
class InputComponent(Component):
    """
    Marks an entity that should react to player input.
    """

    pass
