from dataclasses import dataclass
from ecs_core.component import Component


@dataclass
class InputComponent(Component):
    """
    To tag an entity has a input, input system should respond to the input 
    """

    pass