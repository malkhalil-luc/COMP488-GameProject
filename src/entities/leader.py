from config import SCREEN_WIDTH, FIELD_TOP, COLOR_LEADER
from game_data import LeaderConfig, DEFAULT_LEADER
from ecs_core.entity import Entity
from ecs_core.ecs import World
from components.position import PositionComponent
from components.velocity import VelocityComponent
from components.tag import TagComponent
from components.sprite import SpriteComponent
from components.health import HealthComponent
from components.collider import ColliderComponent
from components.leader_move import LeaderMoveComponent


def _leader_sprite_path(level_index: int) -> str:
    return f"assets/sprites/leader_level{level_index + 1}.png"


def create_leader(
    world: World,
    leader_config: LeaderConfig = DEFAULT_LEADER,
    level_index: int = 0,
) -> Entity:
    """
    Creates the leader for the current level.
    """
    eid = world.create_entity()

    start_x = SCREEN_WIDTH // 2 - leader_config.width // 2
    start_y = FIELD_TOP + 20

    world.add_component(eid, PositionComponent(
        x=float(start_x),
        y=float(start_y),
    ))

    world.add_component(eid, VelocityComponent(vx=0.0, vy=0.0))
    world.add_component(eid, LeaderMoveComponent(
        target_x=float(start_x),
        target_y=float(start_y),
        timer=1,
    ))

    world.add_component(eid, TagComponent(label="leader"))

    world.add_component(eid, SpriteComponent(
        width=leader_config.width,
        height=leader_config.height,
        color=COLOR_LEADER,
        image_path=_leader_sprite_path(level_index),
    ))

    world.add_component(eid, HealthComponent(
        hp=leader_config.hp,
        max_hp=leader_config.hp,
    ))

    world.add_component(eid, ColliderComponent(
        width=leader_config.width,
        height=leader_config.height,
    ))

    return eid
