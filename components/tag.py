#what kind of entity it it

from dataclasses import dataclass
from ecs_core.component import Component


@dataclass
class TagComponent(Component):
    """
    A label identifies what kind of entity 
    label: srt, set by factory, world.add_component(player_id, TagComponent(label="player"))
    """
    label: str