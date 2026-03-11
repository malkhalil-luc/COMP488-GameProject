#entry point
# ─────────────────────────────────────────────
#  main.py  –  COMMIT 1: Render Only
#
#  What this commit proves:
#    ✓ ECS World wired up and running
#    ✓ RenderSystem draws all entities
#    ✓ Player ship at bottom-center
#    ✓ Enemy formation in rows at top
#    ✓ HUD placeholders anchored correctly
#    ✓ Title screen overlay with "Press SPACE to Play"
#    ✗ No input, no movement, no gameplay
# ─────────────────────────────────────────────

import pygame
import sys

from settings import *
from ecs.world      import World
from ecs.components import (
    PositionComponent,
    RenderComponent,
    TagComponent,
    InputComponent,
    ColliderComponent,
)
from ecs.systems import RenderSystem


# ─────────────────────────────────────────────────────────────────────────────
#  Entity factory functions
#  These are plain functions that create an entity in the World and attach
#  the right components to it.  They return the entity ID so main.py can
#  keep a reference if needed (e.g. to move the player later).
# ─────────────────────────────────────────────────────────────────────────────

def create_player(world: World) -> int:
    """
    Player entity:
      - PositionComponent  → placed at bottom-center of playfield
      - RenderComponent    → cyan rectangle
      - TagComponent       → "player"
      - InputComponent     → marks it as keyboard-controlled (used in Commit 2)
      - ColliderComponent  → participates in collision checks (used in Commit 3)
    """
    eid = world.create_entity()
    world.add_component(eid, PositionComponent(
        x = SCREEN_W // 2 - PLAYER_W // 2,
        y = PLAYFIELD_BOT - PLAYER_H - 10,
    ))
    world.add_component(eid, RenderComponent(PLAYER_W, PLAYER_H, PLAYER_COLOR))
    world.add_component(eid, TagComponent("player"))
    world.add_component(eid, InputComponent())
    world.add_component(eid, ColliderComponent(PLAYER_W, PLAYER_H))
    return eid


def create_enemy_formation(world: World) -> list:
    """
    Creates ENEMY_ROWS × ENEMY_COLS enemy entities in a grid.

    Each enemy gets:
      - PositionComponent  → grid position
      - RenderComponent    → red rectangle
      - TagComponent       → "enemy"
      - ColliderComponent  → so projectiles can hit them

    Returns a list of all enemy entity IDs.
    """
    # Centre the formation horizontally
    formation_w = ENEMY_COLS * ENEMY_W + (ENEMY_COLS - 1) * ENEMY_GAP_X
    start_x     = (SCREEN_W - formation_w) // 2
    start_y     = PLAYFIELD_TOP + 20

    enemy_ids = []
    for row in range(ENEMY_ROWS):
        for col in range(ENEMY_COLS):
            eid = world.create_entity()
            x   = start_x + col * (ENEMY_W + ENEMY_GAP_X)
            y   = start_y + row * (ENEMY_H + ENEMY_GAP_Y)

            world.add_component(eid, PositionComponent(x, y))
            world.add_component(eid, RenderComponent(ENEMY_W, ENEMY_H, ENEMY_COLOR))
            world.add_component(eid, TagComponent("enemy"))
            world.add_component(eid, ColliderComponent(ENEMY_W, ENEMY_H))
            enemy_ids.append(eid)

    return enemy_ids


# ─────────────────────────────────────────────────────────────────────────────
#  HUD drawing helpers
#  The HUD is drawn directly with pygame calls for now.
#  (In a fuller ECS we'd make HUD entities too, but let's keep Commit 1 clear.)
# ─────────────────────────────────────────────────────────────────────────────

def draw_hud(screen: pygame.Surface, font: pygame.font.Font,
             score: int, lives: int) -> None:
    """Blit score (top-left) and heart icons (top-right)."""
    # Score — top-left
    score_surf = font.render(f"Score: {score}", True, HUD_TEXT_COLOR)
    screen.blit(score_surf, (10, 16))

    # Lives — top-right, drawn as heart symbols + count
    hearts_text = "♥ " * lives
    lives_surf  = font.render(hearts_text.strip(), True, LIVES_COLOR)
    lives_rect  = lives_surf.get_rect(right=SCREEN_W - 20, top=16)
    screen.blit(lives_surf, lives_rect)

    # Thin separator line under HUD strip
    pygame.draw.line(screen, (60, 60, 80),
                     (0, HUD_HEIGHT - 1), (SCREEN_W, HUD_HEIGHT - 1), 1)


def draw_title_screen(screen: pygame.Surface,
                      title_font: pygame.font.Font,
                      sub_font:   pygame.font.Font) -> None:
    """Semi-transparent overlay with game title and start prompt."""
    # Dark overlay
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    # Title text
    title_surf = title_font.render("INVASION SPACERS", True, (255, 255, 255))
    title_rect = title_surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 30))
    screen.blit(title_surf, title_rect)

    # Subtitle
    sub_surf = sub_font.render("Press SPACE to Play", True, (180, 180, 255))
    sub_rect = sub_surf.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 30))
    screen.blit(sub_surf, sub_rect)


# ─────────────────────────────────────────────────────────────────────────────
#  Main game loop
# ─────────────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # Fonts
    font       = pygame.font.SysFont("monospace", FONT_SIZE)
    title_font = pygame.font.SysFont("monospace", TITLE_FONT_SIZE, bold=True)
    sub_font   = pygame.font.SysFont("monospace", SUB_FONT_SIZE)

    # ── ECS bootstrap ─────────────────────────────────────────────────────
    #
    #  Order matters here:
    #    1. Create the World  (the registry)
    #    2. Create entities and attach components
    #    3. Register systems
    #
    #  In Commit 1, the only system is RenderSystem.
    #  In Commit 2, InputSystem and MovementSystem join.
    #  In Commit 3, CollisionSystem and SpawnSystem join.

    world = World()

    # Create entities (they are just IDs with components attached)
    player_id  = create_player(world)
    enemy_ids  = create_enemy_formation(world)

    # Register systems (Commit 1: render only)
    world.add_system(RenderSystem())

    # ── Game state ────────────────────────────────────────────────────────
    state = "title"   # "title" | "play" | "paused" | "gameover" | "victory"
    score = 0
    lives = 3

    # ── Game loop ─────────────────────────────────────────────────────────
    running = True
    while running:
        # 1. EVENT PROCESSING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # (Commit 2 will handle SPACE → state transition here)

        # 2. UPDATE  (world.update calls every registered system in order)
        #    RenderSystem only needs the screen surface.
        #    Future systems will also receive dt (delta time) and game_state.

        # 3. DRAW
        screen.fill(BG_COLOR)           # clear canvas

        world.update(screen)            # → RenderSystem draws all entities

        draw_hud(screen, font, score, lives)

        if state == "title":
            draw_title_screen(screen, title_font, sub_font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()