from config import FIELD_TOP, FIELD_BOTTOM, SCREEN_WIDTH, PLAYER_HEIGHT, PLAYER_WIDTH, BULLET_H
from ECS_core.system import System
from components.velocity import VelocityComponent
from components.position import PositionComponent
from components.input import InputComponent
from components.lifetime import LifetimeComponent

class MovementSystem(System):
    """
    set velocity to position , clamp player to play field
    """

    def update(self, world, kwargs) -> None:

        if (kwargs.get("game_state")) != "play":
            return

        # set movement
        moving_entities = world.get_entities_with(PositionComponent, VelocityComponent)

        for eid in moving_entities:
            pos = world.get_component(eid,PositionComponent)
            vel = world.get_component(eid, VelocityComponent)

            pos.x += vel.vx
            pos.y += vel.vy

        # clamp player to play field
        player_entities = world.get_entities_with(PositionComponent, InputComponent)

        for eid in player_entities:
            pos = world.get_component(eid,PositionComponent)

            if pos.x < 0: #left edge x must be > 0
                pos.x = 0.0
            if pos.x + PLAYER_WIDTH > SCREEN_WIDTH: # right Edge x must be < screen width
                pos.x = float(SCREEN_WIDTH - PLAYER_WIDTH)

        # remove bullets that reach the HUD
        mortal_entities = world.get_entities_with(PositionComponent, LifetimeComponent)
        for eid in mortal_entities:
            pos = world.get_component(eid, PositionComponent)
            lt  = world.get_component(eid, LifetimeComponent)
            if lt.destroy_when_offscreen:
                if pos.y + BULLET_H < FIELD_TOP:
                    world.remove_entity(eid)