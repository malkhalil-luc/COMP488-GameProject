from ecs_core.ecs import World
from components.position import PositionComponent
from components.velocity import VelocityComponent
from components.tag import TagComponent
from components.sprite import SpriteComponent
from components.lifetime import LifetimeComponent


def create_burst_effect(world: World, x: float, y: float, color: tuple[int, int, int]) -> None:
    particles = [
        (-1.6, -1.2),
        (1.6, -1.2),
        (-0.9, 1.1),
        (0.9, 1.1),
    ]

    for vx, vy in particles:
        eid = world.create_entity()
        world.add_component(eid, PositionComponent(x=x, y=y))
        world.add_component(eid, VelocityComponent(vx=vx, vy=vy))
        world.add_component(eid, TagComponent(label="effect_spark"))
        world.add_component(eid, SpriteComponent(
            width=6,
            height=6,
            color=color,
        ))
        world.add_component(eid, LifetimeComponent(
            destroy_when_offscreen=False,
            frames_left=14,
        ))
