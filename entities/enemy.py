# factory: build the enemy entities

from config import (
    SCREEN_WIDTH, FIELD_TOP,
    ENEMY_WIDTH, ENEMY_HEIGHT,
    ENEMY_ROWS, ENEMY_COLS,
    ENEMY_GAP_X, ENEMY_GAP_Y,
    COLOR_ENEMY,
)
from ECS_core.entity import Entity
from ECS_core.ecs import World
from components.position import PositionComponent
from components.velocity import VelocityComponent
from components.tag import TagComponent
from components.sprite import SpriteComponent
from components.collider import ColliderComponent


def create_enemy_formation(world: World) -> list[Entity]:
    """
    """
    #   formation bounds 

    # Total width of the formation including all gaps
    # 8 enemies = 7 gaps between them → (ENEMY_COLS - 1) gaps
    formation_w = ENEMY_COLS * ENEMY_WIDTH + (ENEMY_COLS - 1) * ENEMY_GAP_X

    # Center the formation horizontally on screen
    start_x = (SCREEN_WIDTH - formation_w) // 2

    # Start just below the HUD 
    start_y = FIELD_TOP + 20

    enemy_ids = []

    for row in range(ENEMY_ROWS):
        for col in range(ENEMY_COLS):

            eid = world.create_entity()

            # Grid position formula
            x = start_x + col * (ENEMY_WIDTH + ENEMY_GAP_X)
            y = start_y + row * (ENEMY_HEIGHT + ENEMY_GAP_Y)

            # Where it is
            world.add_component(eid, PositionComponent(
                x=float(x),
                y=float(y),
            ))

            
            world.add_component(eid, VelocityComponent(vx=0.0, vy=0.0))

            # What kind 
            world.add_component(eid, TagComponent(label="enemy"))

            # What it looks like 
            world.add_component(eid, SpriteComponent(
                width=ENEMY_WIDTH,
                height=ENEMY_HEIGHT,
                color=COLOR_ENEMY,
            ))

            # Collision area 
            world.add_component(eid, ColliderComponent(
                width=ENEMY_WIDTH - 6,
                height=ENEMY_HEIGHT - 4,
            ))

            enemy_ids.append(eid)

    return enemy_ids
