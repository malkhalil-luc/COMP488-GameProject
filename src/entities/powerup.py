from ecs_core.entity import Entity
from ecs_core.ecs import World
from components.position import PositionComponent
from components.velocity import VelocityComponent
from components.tag import TagComponent
from components.sprite import SpriteComponent
from components.collider import ColliderComponent
from components.lifetime import LifetimeComponent


POWERUP_SIZE = 18

POWERUP_COLORS = {
    "powerup_life": (80, 220, 120),
    "powerup_rapid": (80, 180, 255),
    "powerup_shield": (255, 220, 80),
}

POWERUP_LETTERS = {
    "powerup_life": "L",
    "powerup_rapid": "R",
    "powerup_shield": "S",
}

POWERUP_IMAGES = {
    "powerup_life": "assets/sprites/powerup_life.png",
    "powerup_rapid": "assets/sprites/powerup_rapid.png",
    "powerup_shield": "assets/sprites/powerup_shield.png",
}


def create_powerup(world: World, x: float, y: float, kind: str) -> Entity:
    eid = world.create_entity()

    world.add_component(eid, PositionComponent(x=x, y=y))
    world.add_component(eid, VelocityComponent(vx=0.0, vy=1.6))
    world.add_component(eid, TagComponent(label=kind))
    world.add_component(eid, SpriteComponent(
        width=POWERUP_SIZE,
        height=POWERUP_SIZE,
        color=POWERUP_COLORS.get(kind, (200, 200, 200)),
        image_path=POWERUP_IMAGES.get(kind),
    ))
    world.add_component(eid, ColliderComponent(
        width=POWERUP_SIZE,
        height=POWERUP_SIZE,
    ))
    world.add_component(eid, LifetimeComponent(destroy_when_offscreen=True))

    return eid
