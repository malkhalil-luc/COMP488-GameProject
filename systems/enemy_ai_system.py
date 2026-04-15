from ecs_core.system import System
from components.velocity import VelocityComponent
from components.tag import TagComponent
from components.position import PositionComponent
from config import SCREEN_WIDTH, FIELD_TOP, FIELD_BOTTOM
from game_data import DEFAULT_WAVE, DEFAULT_LEADER


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

        wave_config = kwargs.get("wave_config", DEFAULT_WAVE)
        leader_config = kwargs.get("leader_config", DEFAULT_LEADER)
        frame_count = kwargs.get("frame_count", 0)
        
        enemy_count = 0

        tagged_entities = world.get_entities_with(TagComponent, VelocityComponent)

        for eid in tagged_entities:
            tag = world.get_component(eid, TagComponent)
            vel = world.get_component(eid, VelocityComponent)

            if tag.label == "enemy":
                # Regular enemies move down with a simple pattern
                if wave_config.move_pattern == "sway":
                    direction = -1 if (frame_count // 45) % 2 == 0 else 1
                    vel.vx = 1.2 * direction
                elif wave_config.move_pattern == "zigzag":
                    direction = -1 if (frame_count // 25) % 2 == 0 else 1
                    vel.vx = 1.8 * direction
                else:
                    vel.vx = 0.0

                vel.vy = wave_config.speed
                enemy_count += 1

            elif tag.label == "leader":
                # Leader move faster — side to side
                
                pos = world.get_component(eid, PositionComponent)

                # initialise direction on first frame
                if vel.vx == 0.0 and vel.vy == 0.0:
                    vel.vx = leader_config.speed_x
                    vel.vy = leader_config.speed_y

                # bounce off left and right walls
                if pos.x <= 0:
                    vel.vx = abs(vel.vx)
                elif pos.x + leader_config.width >= SCREEN_WIDTH:
                    vel.vx = -abs(vel.vx)

                # bounce off top and bottom of playfield
                if pos.y <= FIELD_TOP:
                    vel.vy = abs(vel.vy)
                elif pos.y + leader_config.height >= FIELD_BOTTOM:
                    vel.vy = -abs(vel.vy)
                    
        leader_alive = kwargs.get("leader_alive", False)

        if enemy_count == 0 and not leader_alive:
            kwargs["wave_cleared"] = True
