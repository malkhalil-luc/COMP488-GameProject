#how fast, which direction (rate of change; how much/amount to move each frame)

from dataclasses import dataclass, field
from ECS_core.component import Component


@dataclass
class VelocityComponent(Component):
    """
    movement rate as how many pixels and entity moves per frame.
    vx: horizontal speed
    vy: vertical speed
    Both default to 0.0, 
    usage: 
        VelocityComponent()           # stationary
        VelocityComponent(vy=-8.0)    # bullet moving up
        VelocityComponent(vx=5.0)     # player moving right
    """

    vx: float = field(default=0.0) # fields to give a default value of a dataclass field
    vy: float = field(default=0.0)