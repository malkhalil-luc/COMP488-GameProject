from dataclasses import dataclass, field
from ecs_core.component import Component


@dataclass
class VelocityComponent(Component):
    """
    movement rate as how many pixels and entity moves per frame.
    vx: horizental speed
    vy: vertical speed
    Both default to 0.0, 
    usage: 
        VelocityComponent()           # stationary
        VelocityComponent(vy=-8.0)    # bullet moving up
        VelocityComponent(vx=5.0)     # player moving right
    """

    vx: float = field(default=0.0) # fields to give a default value of a dataclass field
    vy: float = field(default=0.0)