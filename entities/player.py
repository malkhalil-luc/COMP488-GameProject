# factory: build the player entity

from config import SCREEN_WIDTH, FIELD_BOTTOM, PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, COLOR_PLAYER, STARTING_LIVES
from ECS_core.entity import Entity
from ECS_core.ecs import World
from components.position import PositionComponent
from components.velocity import VelocityComponent
from components.input import InputComponent
from components.tag import TagComponent
from components.sprite import SpriteComponent
from components.health import HealthComponent
from components.collider import ColliderComponent

def create_player(world: World) -> Entity:
    """
    """

    eid = world.create_entity()

    start_x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2   # centered horizontally
    start_y = FIELD_BOTTOM - PLAYER_HEIGHT - 10     # near bottom, 10px margin

    world.add_component(eid, PositionComponent(
        x=float(start_x),
        y=float(start_y),
    ))

    world.add_component(eid, VelocityComponent(vx=0.0, vy=0.0))
    
    world.add_component(eid, VelocityComponent(vx=0.0, vy=0.0))


    world.add_component(eid, InputComponent())

    world.add_component(eid, TagComponent(label="player"))

    world.add_component(eid, SpriteComponent(
        width=PLAYER_WIDTH,
        height=PLAYER_HEIGHT,
        color=COLOR_PLAYER,
    ))

    world.add_component(eid, HealthComponent(
        hp=STARTING_LIVES,
        max_hp=STARTING_LIVES,
    ))

    world.add_component(eid, ColliderComponent(
        width=PLAYER_WIDTH - 8,
        height=PLAYER_HEIGHT - 6,
    ))

    return eid