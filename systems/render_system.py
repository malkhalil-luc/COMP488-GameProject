# called the last

import pygame
from ECS_core.system import System
from components.sprite import SpriteComponent
from components.position import PositionComponent

class RenderSystem(System):
    """
    Draw any visible entity (visible sprite), as a colored rectangle
    Reads: position component, sprint component, and runs the last after all state changes
    """

    def update(self, world, kwargs)-> None:
        """
        Draw entities that has position and sprite and are visible
        kwarge expected: screen: pygame.surface
        """

        screen = kwargs["screen"]
        entities = world.get_entities_with(PositionComponent, SpriteComponent)

        for eid in entities:
            sprite = world.get_component(eid, SpriteComponent)
            if not sprite.visible:
                continue

            pos = world.get_component(eid,PositionComponent)

            rect = pygame.Rect (int(pos.x), int(pos.y), sprite.width, sprite.height)
            pygame.draw.rect(screen,sprite.color,rect)
            pygame.draw.rect(screen,(255,255,255),rect,1)