# when it must be auto destroyed
from dataclasses import dataclass, field
from ecs_core.component import Component

@dataclass
class LifetimeComponent(Component):
    """
    needed to handle entities that are not removed by world remove entity that handles entities after collision.
    destroy flag default to True used in factories for that purpose
            world.add_component(eid, LifetimeComponent())
    """
    destroy_when_offscreen: bool = field(default=True)