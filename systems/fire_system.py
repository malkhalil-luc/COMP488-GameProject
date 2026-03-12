import pygame
from config import PLAYER_WIDTH, BULLET_W
from ecs_core.system import System
from components.position import PositionComponent
from components.input import InputComponent
from entities.bullet import create_bullet


class FireSystem(System):
    """
    Listens for KEYDOWN Space or Shift and spawns a bullet at the
    player's nose position.
    """

    def update(self, world, kwargs) -> None:
        """
        Scan this frame's events for a fire key press.
        If found, spawn one bullet at the player's nose.

        """
        if kwargs.get("game_state") != "play":
            return

        events = kwargs.get("events", [])

        # Check if a fire key was pressed this frame
        fire_pressed = False
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT):
                    fire_pressed = True
                    break  # one bullet per frame regardless of how many keys pressed

        if not fire_pressed:
            return

        #  Find the player entity  it has InputComponent marker 
        player_entities = world.get_entities_with(InputComponent, PositionComponent)

        for eid in player_entities:
            pos = world.get_component(eid, PositionComponent)

            #  Compute bullet spawn position 
            bullet_x = pos.x + PLAYER_WIDTH // 2 - BULLET_W // 2
            bullet_y = pos.y

            #  Spawn the bullet 
            create_bullet(world, bullet_x, bullet_y)