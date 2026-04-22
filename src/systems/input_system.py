import pygame
from config import PLAYER_SPEED
from ecs_core.system import System
from components.velocity import VelocityComponent
from components.input import InputComponent

class InputSystem(System):
    """
    Reads keyboard input and updates the player velocity.
    """

    def update(self, world, kwargs) -> None:
        """
        Handles left and right movement during play.
        """

        if kwargs.get("game_state") != "play":
            return

        keys = pygame.key.get_pressed()

        entities = world.get_entities_with(InputComponent, VelocityComponent)

        for eid in entities:
            vel = world.get_component(eid, VelocityComponent)
            moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

            if moving_left and not moving_right:
                vel.vx = -PLAYER_SPEED
            elif moving_right and not moving_left:
                vel.vx = PLAYER_SPEED
            else:
                vel.vx = 0.0

            vel.vy = 0.0
