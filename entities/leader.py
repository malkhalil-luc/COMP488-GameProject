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


def create_leader(
    world: World,
    leader_config: LeaderConfig = DEFAULT_LEADER,
) -> Entity:
    """
    Build the Enemy Leader entity and return its ID.

    Spawn position: horizontally centered, just below the HUD strip.

    """
    eid = world.create_entity()

    
    # Centered horizontally, near the top of the playfield
    start_x = SCREEN_WIDTH // 2 - leader_config.width // 2
    start_y = FIELD_TOP + 20

    # Where 
    world.add_component(eid, PositionComponent(
        x=float(start_x),
        y=float(start_y),
    ))

    # Velocity starts at 0 — EnemyAISystem sets vy each frame using LEADER_SPEED
    world.add_component(eid, VelocityComponent(vx=0.0, vy=0.0))

    # What kind 
    world.add_component(eid, TagComponent(label="leader"))

    # What it looks like 
    world.add_component(eid, SpriteComponent(
        width=leader_config.width,
        height=leader_config.height,
        color=COLOR_LEADER,
    ))

    # THE KEY DIFFERENCE FROM REGULAR ENEMIES
    # Takes LEADER_HP hits before dying, DamageSystem reads and
    # decrements this. HUD reads hp/max_hp to draw the boss HP bar.
    world.add_component(eid, HealthComponent(
        hp=leader_config.hp,
        max_hp=leader_config.hp,
    ))

    # Collision area
    world.add_component(eid, ColliderComponent(
        width=leader_config.width,
        height=leader_config.height,
    ))

    return eid
