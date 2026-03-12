import pygame
from config import PLAYER_SPEED
from ECS_core.system import System
from components.velocity import VelocityComponent
from components.input import InputComponent

class InputSystem(System):
    """
    """

    def update (self, world, kwargs) -> None:
        """
        """

        #gate, only in play mode
        if kwargs.get("game_state") != "play":
            return

        keys = pygame.key.get_pressed() # real all keyboard state

        entities = world.get_entities_with(InputComponent, VelocityComponent)

        for eid in entities:
            vel = world.get_component(eid, VelocityComponent)
            moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

            if moving_left and not moving_right:
                vel.vx = -PLAYER_SPEED
            elif moving_right and not moving_left:
                vel.vx = PLAYER_SPEED
            else: # as if non pressed or pressed together
                vel.vx = 0.0

            vel.vy = 0.0 # can be changed later if vertical movement added.
