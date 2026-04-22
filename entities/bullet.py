from config import BULLET_W, BULLET_H, BULLET_SPEED, COLOR_BULLET
from ecs_core.entity import Entity
from ecs_core.ecs import World
from components.position import PositionComponent
from components.velocity import VelocityComponent
from components.tag import TagComponent
from components.sprite import SpriteComponent
from components.collider import ColliderComponent
from components.lifetime import LifetimeComponent


def create_bullet(
    world: World,
    x: float,
    y: float,
    *,
    vx: float = 0.0,
    vy: float = -BULLET_SPEED,
    label: str = "player_bullet",
    color: tuple[int, int, int] = COLOR_BULLET,
    image_path: str | None = None,
) -> Entity:
    """
    Creates one bullet entity at the given position.
    """
    eid = world.create_entity()

    world.add_component(eid, PositionComponent(x=x, y=y))

    world.add_component(eid, VelocityComponent(
        vx=vx,
        vy=vy,
    ))

    world.add_component(eid, TagComponent(label=label))

    world.add_component(eid, SpriteComponent(
        width=BULLET_W,
        height=BULLET_H,
        color=color,
        image_path=image_path,
    ))

    world.add_component(eid, ColliderComponent(
        width=BULLET_W,
        height=BULLET_H,
    ))

    world.add_component(eid, LifetimeComponent(destroy_when_offscreen=True))

    return eid
