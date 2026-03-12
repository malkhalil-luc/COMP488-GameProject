from config import ENEMY_SPEED, LEADER_SPEED
from ECS_core.system import System
from components.velocity import VelocityComponent
from components.tag import TagComponent

class EnemyAISystem(System):
    """
    Sets enemy and leader velocities each frame.
    Signals game.py when the wave is cleared.
    """
    def update (self,world,kwargs) -> None:
        """
        """
        if kwargs.get("game_state") != "play":
            return
        
        enemy_count = 0

        tagged_entities = world.get_entities_with(TagComponent, VelocityComponent)

        for eid in tagged_entities:
            tag = world.get_component(eid, TagComponent)
            vel = world.get_component(eid, VelocityComponent)

            if tag.label == "enemy":
                # Regular enemies move down
                vel.vy = ENEMY_SPEED
                vel.vx = 0.0
                enemy_count += 1

            elif tag.label == "leader":
                # Leader move faster — side to side
                from components.position import PositionComponent
                from config import LEADER_WIDTH, LEADER_HEIGHT, SCREEN_WIDTH, FIELD_TOP, FIELD_BOTTOM, LEADER_SPEED_X, LEADER_SPEED_Y

                pos = world.get_component(eid, PositionComponent)

                # initialise direction on first frame
                if vel.vx == 0.0 and vel.vy == 0.0:
                    vel.vx = LEADER_SPEED_X
                    vel.vy = LEADER_SPEED_Y

                # bounce off left and right walls
                if pos.x <= 0:
                    vel.vx = abs(vel.vx)
                elif pos.x + LEADER_WIDTH >= SCREEN_WIDTH:
                    vel.vx = -abs(vel.vx)

                # bounce off top and bottom of playfield
                if pos.y <= FIELD_TOP:
                    vel.vy = abs(vel.vy)
                elif pos.y + LEADER_HEIGHT >= FIELD_BOTTOM:
                    vel.vy = -abs(vel.vy)
                    
        leader_alive = kwargs.get("leader_alive", False)

        if enemy_count == 0 and not leader_alive:
            kwargs["wave_cleared"] = True