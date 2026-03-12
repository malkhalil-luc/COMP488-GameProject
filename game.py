#state machine + orchestration
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    HUD_H, BOSS_BAR_H, FIELD_TOP, FIELD_BOTTOM,
    COLOR_BG, COLOR_PLAYER, COLOR_ENEMY, COLOR_LEADER, COLOR_BULLET,
    FONT_SIZE, FONT_TITLE_SIZE, FONT_SUB_SIZE,
    STARTING_LIVES, SCORE_ENEMY, SCORE_LEADER,
    LEADER_WIDTH, LEADER_HEIGHT,
)
from ECS_core.ecs import World
from systems.input_system import InputSystem
from systems.fire_system import FireSystem
from systems.enemy_ai_system import EnemyAISystem
from systems.movement_system import MovementSystem
from systems.collision_system import CollisionSystem
from systems.damage_system import DamageSystem
from systems.render_system import RenderSystem
from entities.player import create_player
from entities.enemy import create_enemy_formation
from entities.leader import create_leader
from components.sprite import SpriteComponent
from components.input import InputComponent


class Game:
    """
    Owns the state machine, game variables, world, and frame loop.

    Call game.run() from main.py to start.
    """

    def __init__(self) -> None:
        #  pygame setup 
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        #  fonts 
        self.font       = pygame.font.SysFont(None, FONT_SIZE)
        self.font_title = pygame.font.SysFont(None, FONT_TITLE_SIZE)
        self.font_sub   = pygame.font.SysFont(None, FONT_SUB_SIZE)

        #  ECS world 
        self.world = World()
        self._register_systems()

        #  game state 
        self.state = "title"

        #  game variables 
        # Initialised here, reset on every new run via _reset()
        self.score       = 0
        self.lives       = STARTING_LIVES
        self.leader_alive = False
        self.leader_hit_cooldown = 0

        # Entity IDs — stored so game.py can reference them if needed
        self.player_eid  = None
        self.enemy_eids  = []

        self.player_flash_timer = 0

        self.heart_img = pygame.image.load("assets/sprites/heart.png").convert_alpha()
        self.heart_img = pygame.transform.scale(self.heart_img, (20, 20))



    def _register_systems(self) -> None:
        """
        Register all systems in execution order.
        Order is critical — see module docstring.
        """
        self.world.add_system(InputSystem())
        self.world.add_system(FireSystem())
        self.world.add_system(EnemyAISystem())
        self.world.add_system(MovementSystem())
        self.world.add_system(CollisionSystem())
        self.world.add_system(DamageSystem())
        self.world.add_system(RenderSystem())

    def _reset(self) -> None:
        """
        Reset all game variables and rebuild the world for a fresh run.

        Called when starting from title screen and on restart from
        gameover or victory screen.

        Steps:
            1. Reset score, lives, leader flag
            2. Clear the entire world (remove all entities)
            3. Spawn fresh player + enemy formation
        """
        self.score        = 0
        self.lives        = STARTING_LIVES
        self.leader_alive = False
        self.leader_hit_cooldown = 0
        self.player_flash_timer = 0

        # clear existing entities from the world
        self.world.clear()

        # Spawn initial entities via factories
        self.player_eid = create_player(self.world)
        self.enemy_eids = create_enemy_formation(self.world)


    def run(self) -> None:
        """
        Main game loop. Called from main.py.
        Runs until the player closes the window.
        """
        running = True

        while running:
            #  Collect events 
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    running = False

                #  State machine input (game state transitions)
                # InputSystem only handles entity velocity

                if event.type == pygame.KEYDOWN:

                    # Title screen → start game
                    if self.state == "title" and event.key == pygame.K_SPACE:
                        self._reset()
                        self.state = "play"
                        events = []

                    # Play → pause / pause → play
                    elif event.key in (pygame.K_p, pygame.K_ESCAPE):
                        if self.state == "play":
                            self.state = "paused"
                        elif self.state == "paused":
                            self.state = "play"

                    # Gameover or victory → restart
                    elif event.key == pygame.K_r:
                        if self.state in ("gameover", "victory"):
                            self._reset()
                            self.state = "play"

            #  Clear screen 
            self.screen.fill(COLOR_BG)

            # Build kwargs for this dict frame 
            # Systems read from and write back to this dict.
            fDict_kwargs = {
                "screen":       self.screen,
                "events":       events,
                "game_state":   self.state,
                "score":        self.score,
                "lives":        self.lives,
                "leader_alive": self.leader_alive,
                "leader_hit_cooldown":  self.leader_hit_cooldown,
            }

            #  Update world (runs all systems in order) 
            self.world.update(fDict_kwargs)
            self.leader_hit_cooldown = fDict_kwargs.get("leader_hit_cooldown", 0)
            if self.leader_hit_cooldown > 0:
                self.leader_hit_cooldown -= 1

            ### flash the player sprite when hit
            if fDict_kwargs.get("lives", self.lives) < self.lives:
                self.player_flash_timer = 60  # 1 seconds of flashing

            if self.player_flash_timer > 0:
                self.player_flash_timer -= 1
                # toggle visible every 6 frames — creates a flash effect

                player_entities = self.world.get_entities_with(InputComponent, SpriteComponent)
                for eid in player_entities:
                    sprite = self.world.get_component(eid, SpriteComponent)
                    sprite.visible = (self.player_flash_timer % 6) < 3
            else:
                # make sure player is always visible when not flashing
                player_entities = self.world.get_entities_with(InputComponent, SpriteComponent)
                for eid in player_entities:
                    sprite = self.world.get_component(eid, SpriteComponent)
                    sprite.visible = True

                ###

            #  Read signals written by systems
            # Score and lives may have been updated by DamageSystem
            self.score = fDict_kwargs.get("score", self.score)
            self.lives = fDict_kwargs.get("lives", self.lives)

            # Wave cleared → spawn the leader
            if fDict_kwargs.get("wave_cleared") and not self.leader_alive:
                create_leader(self.world)
                self.leader_alive = True

            # State transitions triggered by DamageSystem
            if fDict_kwargs.get("trigger_victory"):
                self.state = "victory"
                self.leader_alive = False

            if fDict_kwargs.get("trigger_gameover"):
                self.state = "gameover"

            #  Draw HUD on top of entities 
            # RenderSystem drew entities. Now game.py draws UI on top.
            if self.state in ("play", "paused"):
                self._draw_hud()

            #  Draw state overlays 
            if self.state == "title":
                self._draw_title_overlay()
            elif self.state == "paused":
                self._draw_pause_overlay()
            elif self.state == "gameover":
                self._draw_gameover_overlay()
            elif self.state == "victory":
                self._draw_victory_overlay()

            pygame.display.flip()
            self.clock.tick(FPS)


    def _draw_hud(self) -> None:
        """
        Draw the HUD strip at the top of the screen.
        Score on the left, lives on the right.
        Boss HP bar at the bottom when leader is alive.
        """
       
        #  Score (top-left) 
        score_surf = self.font.render(f"Score: {self.score}", True, (240, 240, 240))
        self.screen.blit(score_surf, score_surf.get_rect(topleft=(12, 14)))

        #  Lives (top-right) — shown as heart count  
        for i in range(self.lives):
            hx = SCREEN_WIDTH - 20 - i * 26
            self.screen.blit(self.heart_img, (hx - 20 , 12))

        # HUD divider line 
        pygame.draw.line(
            self.screen, (60, 60, 80),
            (0, HUD_H - 2), (SCREEN_WIDTH, HUD_H - 2), 3
        )

        #  Boss HP bar (bottom strip — only during leader phase) 
        if self.leader_alive:
            self._draw_boss_bar()

    def _draw_boss_bar(self) -> None:
        """
        Draw the Enemy Leader HP bar at the bottom of the screen.
        Reads HealthComponent from the leader entity directly.
        """
        from components.health import HealthComponent
        from components.tag import TagComponent

        # Find the leader entity to read current HP
        leader_entities = self.world.get_entities_with(TagComponent, HealthComponent)
        leader_hp  = 0
        leader_max = 1  # avoid divide-by-zero

        for eid in leader_entities:
            tag = self.world.get_component(eid, TagComponent)
            if tag.label == "leader":
                health = self.world.get_component(eid, HealthComponent)
                leader_hp  = health.hp
                leader_max = health.max_hp
                break

        # Bar dimensions — centered at the bottom strip
        bar_w   = 300
        bar_h   = 18
        bar_x   = SCREEN_WIDTH // 2 - bar_w // 2
        bar_y   = SCREEN_HEIGHT - BOSS_BAR_H + (BOSS_BAR_H - bar_h) // 2

        # Background track
        track_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
        pygame.draw.rect(self.screen, (60, 20, 20), track_rect)

        # Fill — scales with hp / max_hp
        pct      = leader_hp / leader_max
        fill_w   = int(bar_w * pct)
        fill_rect = pygame.Rect(bar_x, bar_y, fill_w, bar_h)
        pygame.draw.rect(self.screen, COLOR_LEADER, fill_rect)

        # Outline
        pygame.draw.rect(self.screen, (200, 200, 200), track_rect, 2)

        # Label
        label = self.font.render(f"LEADER  {leader_hp}/{leader_max}", True, (240, 240, 240))
        self.screen.blit(label, label.get_rect(
            centerx=SCREEN_WIDTH // 2,
            bottom=bar_y - 4,
        ))


    def _draw_overlay_panel(self) -> pygame.Rect:
        """
        Draw a semi-transparent dark panel in the center of the screen.
        Returns the panel rect so callers can position text inside it.
        """
        panel = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 120, 440, 240)
        dark  = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        dark.fill((10, 10, 20, 210))
        self.screen.blit(dark, panel.topleft)
        pygame.draw.rect(self.screen, (100, 100, 140), panel, 2)
        return panel

    def _draw_title_overlay(self) -> None:
        panel = self._draw_overlay_panel()

        title = self.font_title.render("INVASION SPACERS", True, (0, 200, 255))
        self.screen.blit(title, title.get_rect(centerx=panel.centerx, top=panel.top + 30))

        sub = self.font_sub.render("Press SPACE to Play", True, (200, 200, 200))
        self.screen.blit(sub, sub.get_rect(centerx=panel.centerx, top=panel.top + 100))

        hint = self.font.render("Arrow keys / WASD — move    Space / Shift — fire    P — pause", True, (140, 140, 160))
        self.screen.blit(hint, hint.get_rect(centerx=panel.centerx, top=panel.top + 160))
        
        hint = self.font.render("COMP 323/488 TEAM E", True, (140, 140, 160))
        self.screen.blit(hint, hint.get_rect(centerx=panel.centerx, top=panel.top + 200))

    def _draw_pause_overlay(self) -> None:
        panel = self._draw_overlay_panel()

        paused = self.font_title.render("PAUSED", True, (240, 240, 100))
        self.screen.blit(paused, paused.get_rect(centerx=panel.centerx, top=panel.top + 50))

        resume = self.font_sub.render("Press P or ESC to Resume", True, (200, 200, 200))
        self.screen.blit(resume, resume.get_rect(centerx=panel.centerx, top=panel.top + 130))

    def _draw_gameover_overlay(self) -> None:
        panel = self._draw_overlay_panel()

        title = self.font_title.render("GAME OVER", True, (220, 60, 60))
        self.screen.blit(title, title.get_rect(centerx=panel.centerx, top=panel.top + 30))

        score = self.font_sub.render(f"Final Score: {self.score}", True, (240, 240, 240))
        self.screen.blit(score, score.get_rect(centerx=panel.centerx, top=panel.top + 100))

        restart = self.font.render("Press R to Restart", True, (180, 180, 180))
        self.screen.blit(restart, restart.get_rect(centerx=panel.centerx, top=panel.top + 160))

    def _draw_victory_overlay(self) -> None:
        panel = self._draw_overlay_panel()

        title = self.font_title.render("VICTORY!", True, (100, 220, 100))
        self.screen.blit(title, title.get_rect(centerx=panel.centerx, top=panel.top + 30))

        score = self.font_sub.render(f"Final Score: {self.score}", True, (240, 240, 240))
        self.screen.blit(score, score.get_rect(centerx=panel.centerx, top=panel.top + 100))

        restart = self.font.render("Press R to Play Again", True, (180, 180, 180))
        self.screen.blit(restart, restart.get_rect(centerx=panel.centerx, top=panel.top + 160))