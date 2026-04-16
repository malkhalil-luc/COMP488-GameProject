import pygame
from ecs_core.system import System
from components.sprite import SpriteComponent
from components.position import PositionComponent
from components.tag import TagComponent
from entities.powerup import POWERUP_LETTERS

class RenderSystem(System):
    """
    Draws visible entities on the screen.
    """

    def __init__(self) -> None:
        self.label_font = pygame.font.SysFont(None, 18)

    def update(self, world, kwargs)-> None:
        """
        Draws every entity that has a position and a sprite.
        """

        screen = kwargs["screen"]
        entities = world.get_entities_with(PositionComponent, SpriteComponent)

        for eid in entities:
            sprite = world.get_component(eid, SpriteComponent)
            if not sprite.visible:
                continue

            pos = world.get_component(eid,PositionComponent)
            tag = world.get_component(eid, TagComponent)

            rect = pygame.Rect (int(pos.x), int(pos.y), sprite.width, sprite.height)

            if tag is not None and tag.label == "effect_spark":
                pygame.draw.circle(screen, sprite.color, rect.center, max(2, sprite.width // 2))
                continue

            if tag is not None and tag.label.startswith("powerup_"):
                pygame.draw.rect(screen, sprite.color, rect)
                pygame.draw.rect(screen,(255,255,255),rect,2)
                inner_rect = rect.inflate(-6, -6)
                pygame.draw.rect(screen, (20, 20, 30), inner_rect)
                label_text = POWERUP_LETTERS.get(tag.label, "?")
                label_surf = self.label_font.render(label_text, True, sprite.color)
                label_rect = label_surf.get_rect(center=rect.center)
                screen.blit(label_surf, label_rect)
                continue

            pygame.draw.rect(screen,sprite.color,rect)
            pygame.draw.rect(screen,(255,255,255),rect,1)
