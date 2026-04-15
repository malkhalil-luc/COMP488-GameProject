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
) -> Entity:
    """
    Build a single bullet entity at the given position.

    Called by ShootingSystem each time the player fires.
    x, y should be the player's nose position:
        x = player_pos.x + PLAYER_W // 2 - BULLET_W // 2
        y = player_pos.y

    Returns:
        Entity — the bullet's unique ID in the world registry
    """
    eid = world.create_entity()

    # Where it spawns 
    world.add_component(eid, PositionComponent(x=x, y=y))

    world.add_component(eid, VelocityComponent(
        vx=vx,
        vy=vy,
    ))

    # What kind of entity this is
    world.add_component(eid, TagComponent(label=label))

    # What it looks like — small yellow rectangle
    world.add_component(eid, SpriteComponent(
        width=BULLET_W,
        height=BULLET_H,
        color=color,
    ))

    # Collision area — matches sprite exactly for bullets
    world.add_component(eid, ColliderComponent(
        width=BULLET_W,
        height=BULLET_H,
    ))

    # Auto-destroy, MovementSystem checks this flag and calls world.remove_entity()
    world.add_component(eid, LifetimeComponent(destroy_when_offscreen=True))

    return eid
